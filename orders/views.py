from decimal import Decimal
from typing import Dict
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from menu.models import MenuItem
from tables.models import Table
from .models import Order, OrderItem


def _get_cart(session) -> Dict[str, int]:
    """
    获取购物车数据 (辅助函数)
    
    从 session 中获取 'cart' 字典，如果不存在或格式错误则返回空字典
    
    参数:
    - session: request.session 对象
    
    返回:
    - 字典: {商品ID(str): 数量(int)}
    """
    cart = session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    return cart


def _cart_count(cart: Dict[str, int]) -> int:
    """
    计算购物车商品总数 (辅助函数)
    
    参数:
    - cart: 购物车字典
    
    返回:
    - int: 商品总数量
    """
    return sum(cart.values())


@require_POST
def cart_add(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    添加商品到购物车 (HTMX 接口)
    
    功能:
    1. 将指定商品数量 +1
    2. 返回更新后的购物车总数、当前商品数量、减少按钮的 HTML 片段 (OOB swap)
    
    参数:
    - item_id: 商品 ID
    
    返回:
    - 包含多个 HTMX OOB (Out of Band) 更新片段的 HTML 字符串
    """
    cart = _get_cart(request.session)
    key = str(item_id)
    cart[key] = cart.get(key, 0) + 1
    request.session["cart"] = cart
    count = _cart_count(cart)
    current_qty = cart.get(key, 0)
    dec_url = reverse("orders:cart-dec", args=[item_id])
    minus_fragment = (
        f'<div id="minus-{item_id}" hx-swap-oob="true" class="minus-circle">'
        f'<button hx-post="{dec_url}" hx-swap="none" aria-controls="qty-{item_id}" aria-label="Remove">−</button>'
        f'</div>'
        if current_qty > 0
        else
        f'<div id="minus-{item_id}" hx-swap-oob="true" class="minus-circle" style="display:none">'
        f'<button hx-post="{dec_url}" hx-swap="none" aria-controls="qty-{item_id}" aria-label="Remove">−</button>'
        f'</div>'
    )
    return HttpResponse(
        f'<span id="cart-count" hx-swap-oob="true">{count}</span>'
        f'<span id="qty-{item_id}" hx-swap-oob="true">{current_qty}</span>'
        f'{minus_fragment}'
        f'<div id="cart-live" hx-swap-oob="true" class="visually-hidden">Cart items: {count}</div>'
    )


@require_POST
def cart_dec(request: HttpRequest, item_id: int) -> HttpResponse:
    """
    从购物车减少商品 (HTMX 接口)
    
    功能:
    1. 将指定商品数量 -1，如果数量为 0 则移除
    2. 返回更新后的购物车总数、当前商品数量、减少按钮的 HTML 片段 (OOB swap)
    
    参数:
    - item_id: 商品 ID
    
    返回:
    - 包含多个 HTMX OOB (Out of Band) 更新片段的 HTML 字符串
    """
    cart = _get_cart(request.session)
    key = str(item_id)
    if key in cart:
        cart[key] = max(0, cart[key] - 1)
        if cart[key] == 0:
            del cart[key]
    request.session["cart"] = cart
    count = _cart_count(cart)
    current_qty = cart.get(key, 0)
    dec_url = reverse("orders:cart-dec", args=[item_id])
    minus_fragment = (
        f'<div id="minus-{item_id}" hx-swap-oob="true" class="minus-circle">'
        f'<button hx-post="{dec_url}" hx-swap="none" aria-controls="qty-{item_id}" aria-label="Remove">−</button>'
        f'</div>'
        if current_qty > 0
        else
        f'<div id="minus-{item_id}" hx-swap-oob="true" class="minus-circle" style="display:none">'
        f'<button hx-post="{dec_url}" hx-swap="none" aria-controls="qty-{item_id}" aria-label="Remove">−</button>'
        f'</div>'
    )
    return HttpResponse(
        f'<span id="cart-count" hx-swap-oob="true">{count}</span>'
        f'<span id="qty-{item_id}" hx-swap-oob="true">{current_qty}</span>'
        f'{minus_fragment}'
        f'<div id="cart-live" hx-swap-oob="true" class="visually-hidden">Cart items: {count}</div>'
    )


def cart_view(request: HttpRequest) -> HttpResponse:
    """
    查看购物车页面
    
    功能:
    - 计算购物车中所有商品的总价和明细
    - 渲染购物车页面
    
    返回:
    - 渲染 orders/cart.html
    """
    cart = _get_cart(request.session)
    ids = [int(k) for k in cart.keys()]
    items = list(MenuItem.objects.filter(id__in=ids))
    id_map = {i.id: i for i in items}
    lines = []
    total = Decimal("0.00")
    for k, qty in cart.items():
        item = id_map.get(int(k))
        if item:
            line_total = item.price * qty
            lines.append({"item": item, "qty": qty, "line_total": line_total})
            total += line_total
    return render(request, "orders/cart.html", {"lines": lines, "total": total})


@require_POST
@login_required
def checkout(request: HttpRequest) -> HttpResponse:
    """
    结账视图
    
    功能:
    - 创建订单 (Order) 和订单项 (OrderItem)
    - 清空购物车
    
    返回:
    - 成功: 渲染 orders/order_success.html
    - 失败 (购物车为空): 重定向回购物车页面
    """
    cart = _get_cart(request.session)
    if not cart:
        return redirect("orders:cart")

    total_price = Decimal("0.00")
    # Simple logic: assume table 1 for now or get from session/user if available
    # In a real app, user might scan a QR code to set table_id
    table = Table.objects.first() 
    
    order = Order.objects.create(
        user=request.user,
        table=table,
        total_price=Decimal("0.00"),
        status="pending"
    )

    ids = [int(k) for k in cart.keys()]
    items = MenuItem.objects.filter(id__in=ids)
    item_map = {i.id: i for i in items}

    for item_id_str, qty in cart.items():
        item = item_map.get(int(item_id_str))
        if item:
            price = item.price * qty
            OrderItem.objects.create(
                order=order,
                menu_item=item,
                quantity=qty,
                price=item.price
            )
            total_price += price

    order.total_price = total_price
    order.save()

    # Clear cart
    request.session["cart"] = {}
    
    return render(request, "orders/order_success.html", {"order": order})
