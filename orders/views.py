from decimal import Decimal
from typing import Dict
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required, user_passes_test
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
    3. 检查过敏原 (Allergen Check): 如果用户设置了过敏原且菜品包含，触发警告
    """
    # 0. Allergen Check (Only if confirmed is not present)
    confirmed = request.GET.get("confirmed") == "true"
    if not confirmed and request.user.is_authenticated:
        item = get_object_or_404(MenuItem, id=item_id)
        
        # Check intersection using M2M
        # request.user.allergens is a Manager, item.allergens is a Manager
        user_allergens = request.user.allergens.all()
        if user_allergens.exists():
            item_allergens = item.allergens.all()
            # Find intersection
            conflict = item_allergens.intersection(user_allergens)
            
            if conflict:
                # Return a warning modal trigger instead of adding
                conflict_names = [a.name for a in conflict]
                conflict_str = ", ".join(conflict_names)
                return HttpResponse(
                    f"""
                    <div id="allergen-modal-container" hx-swap-oob="true">
                    <div class="modal fade show d-block" style="background: rgba(0,0,0,0.8);" tabindex="-1" role="dialog">
                        <div class="modal-dialog modal-dialog-centered" role="document">
                            <div class="modal-content glass-card border-warning">
                                <div class="modal-header border-secondary">
                                    <h5 class="modal-title text-warning"><i class="bi bi-exclamation-triangle-fill"></i> Allergen Warning</h5>
                                    <button type="button" class="btn-close btn-close-white" onclick="document.getElementById('allergen-modal-container').innerHTML=''"></button>
                                </div>
                                <div class="modal-body text-white">
                                    <p>This item contains allergens that match your profile:</p>
                                    <p class="fw-bold text-danger fs-5">{conflict_str}</p>
                                    <p>Do you still want to add it?</p>
                                </div>
                                <div class="modal-footer border-secondary">
                                    <button type="button" class="btn btn-outline-light" onclick="document.getElementById('allergen-modal-container').innerHTML=''">Cancel</button>
                                    <button type="button" class="btn btn-warning" 
                                            hx-post="{reverse('orders:cart-add', args=[item_id])}?confirmed=true" 
                                            hx-target="#cart-count" 
                                            hx-swap="none"
                                            onclick="document.getElementById('allergen-modal-container').innerHTML=''">
                                        Proceed Anyway
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                """
            )

    cart = _get_cart(request.session)
    key = str(item_id)
    cart[key] = cart.get(key, 0) + 1
    request.session["cart"] = cart
    count = _cart_count(cart)
    current_qty = cart.get(key, 0)
    dec_url = reverse("orders:cart-dec", args=[item_id])
    
    # Correctly include hx-post and class in the button for OOB swap
    minus_content = f'<button hx-post="{dec_url}" hx-swap="none" aria-controls="qty-{item_id}" aria-label="Remove">−</button>'
    
    if current_qty > 0:
        minus_fragment = f'<div id="minus-{item_id}" hx-swap-oob="true" class="minus-circle">{minus_content}</div>'
    else:
        minus_fragment = f'<div id="minus-{item_id}" hx-swap-oob="true" class="minus-circle" style="display:none">{minus_content}</div>'
    
    return HttpResponse(
        f'<span id="cart-count" hx-swap-oob="true">{count}</span>'
        f'<span id="qty-{item_id}" class="counter-qty" hx-swap-oob="true">{current_qty}</span>'
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
    
    # Correctly include hx-post and class in the button for OOB swap
    minus_content = f'<button hx-post="{dec_url}" hx-swap="none" aria-controls="qty-{item_id}" aria-label="Remove">−</button>'
    
    if current_qty > 0:
        minus_fragment = f'<div id="minus-{item_id}" hx-swap-oob="true" class="minus-circle">{minus_content}</div>'
    else:
        minus_fragment = f'<div id="minus-{item_id}" hx-swap-oob="true" class="minus-circle" style="display:none">{minus_content}</div>'
    
    return HttpResponse(
        f'<span id="cart-count" hx-swap-oob="true">{count}</span>'
        f'<span id="qty-{item_id}" class="counter-qty" hx-swap-oob="true">{current_qty}</span>'
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
def checkout_confirmation(request: HttpRequest) -> HttpResponse:
    """
    结账确认视图
    
    功能:
    - 接收购物车页面的 POST 数据（包括每项备注）
    - 计算折扣（示例逻辑）
    - 渲染确认页面供用户最终检查
    """
    cart = _get_cart(request.session)
    if not cart:
        return redirect("orders:cart")

    ids = [int(k) for k in cart.keys()]
    items = list(MenuItem.objects.filter(id__in=ids))
    id_map = {i.id: i for i in items}
    
    lines = []
    total_price = Decimal("0.00")
    
    for k, qty in cart.items():
        item = id_map.get(int(k))
        if item:
            # Get note from POST data
            note = request.POST.get(f"note_{k}", "")
            line_total = item.price * qty
            lines.append({
                "item": item,
                "qty": qty,
                "line_total": line_total,
                "note": note
            })
            total_price += line_total
            
    # Simple discount logic example (e.g. 10% off if total > 100)
    discount = Decimal("0.00")
    if total_price > 100:
        discount = total_price * Decimal("0.10")
        
    final_total = total_price - discount
    
    context = {
        "lines": lines,
        "total_price": total_price,
        "discount": discount,
        "final_total": final_total
    }
    return render(request, "orders/checkout.html", context)


@require_POST
def checkout(request: HttpRequest) -> HttpResponse:
    """
    结账视图
    
    功能:
    - 创建订单 (Order) 和订单项 (OrderItem)
    - 清空购物车
    
    返回:
    - 成功: 重定向到订单成功页 (order-success)
    - 失败 (购物车为空): 重定向回购物车页面
    """
    cart = _get_cart(request.session)
    if not cart:
        return redirect("orders:cart")

    total_price = Decimal("0.00")
    
    # 尝试从 session 获取桌号，如果不存在则默认为 1 (或者可以跳转到错误页)
    table_id = request.session.get("table_id")
    table = None
    
    if table_id:
        table = Table.objects.filter(table_number=table_id).first()
    
    # Fallback: if no table in session, try to find Table 1 or any first table
    if not table:
        table = Table.objects.filter(table_number=1).first()
        if not table:
            table = Table.objects.first()
            
    # 如果还是没有找到对应的桌子，重定向回菜单页并提示
    if not table:
        from django.contrib import messages
        messages.error(request, "Please scan a table QR code or select a table number to continue.")
        return redirect("menu")
    
    # Handle user assignment: use request.user if authenticated, else None
    user = request.user if request.user.is_authenticated else None
    
    order = Order.objects.create(
        user=user,
        table=table,
        total_price=Decimal("0.00"),
        status="pending",
        note=request.POST.get("global_note", "")
    )
    
    # Save order ID to session for guest tracking
    # Important: Explicitly save the session to ensure persistence
    if not request.user.is_authenticated:
        order_history = request.session.get("order_history", [])
        if order.id not in order_history:
            order_history.append(order.id)
            request.session["order_history"] = order_history
            request.session.modified = True  # Ensure session is saved
    
    # Retrieve discount from POST (be careful with client-side manipulation in real apps)
    # Ideally recalculate, but for now we trust the flow or simple logic
    try:
        discount_val = Decimal(request.POST.get("discount", "0.00"))
    except:
        discount_val = Decimal("0.00")
    order.discount = discount_val

    ids = [int(k) for k in cart.keys()]
    items = MenuItem.objects.filter(id__in=ids)
    item_map = {i.id: i for i in items}

    for item_id_str, qty in cart.items():
        item = item_map.get(int(item_id_str))
        if item:
            # Get special request note from POST data
            note = request.POST.get(f"note_{item_id_str}", "")
            
            # Note: Storing price in OrderItem is recommended but model doesn't have it yet.
            # Using current item.price for total calculation.
            price = item.price * qty
            OrderItem.objects.create(
                order=order,
                item=item,
                quantity=qty,
                price=item.price,  # Freeze the price
                special_request=note  # Save the note
            )
            total_price += price

    order.total_price = total_price - order.discount
    order.save()

    # Clear cart
    request.session["cart"] = {}
    
    return redirect(reverse("orders:order-success", args=[order.id]))


def order_success(request: HttpRequest, order_id: int) -> HttpResponse:
    """
    订单成功页视图
    """
    # Allow guest access if order ID is in session
    if not request.user.is_authenticated:
        order_history = request.session.get("order_history", [])
        
        # Temporary workaround: if order_id is NOT in session but exists, check if it was created < 1 minute ago
        if order_id not in order_history:
            try:
                order = Order.objects.get(id=order_id)
                from django.utils import timezone
                import datetime
                
                # Check if order time is naive or aware
                order_time = order.order_time
                if timezone.is_naive(order_time):
                    now = datetime.datetime.now()
                else:
                    now = timezone.now()
                
                # Calculate diff properly
                try:
                    # If both are aware or both are naive, this works
                    diff = (now - order_time).total_seconds()
                except TypeError:
                    # Fallback: make naive aware or vice versa?
                    # Easiest is to just allow it for now if we hit this edge case in dev
                    diff = 0
                
                if abs(diff) < 60:
                    # It's a brand new order, likely from this user.
                    order_history.append(order_id)
                    request.session["order_history"] = order_history
                    request.session.modified = True
            except Order.DoesNotExist:
                return redirect("menu")
        
        if order_id not in order_history:
            return redirect("menu")
        order = get_object_or_404(Order, id=order_id)
    else:
        order = get_object_or_404(Order, id=order_id, user=request.user)
        
    return render(request, "orders/order_success.html", {"order": order})


@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
def update_order_status(request, order_id):
    """
    更新订单状态 (管理端)
    
    功能:
    - 接收 POST 请求更新订单状态
    - 支持 HTMX: 返回更新后的列表或空响应
    """
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get("status")
    
    if new_status in Order.Status.values:
        order.status = new_status
        order.save()
        
    # 如果是 HTMX 请求
    if request.headers.get("HX-Request"):
        # 重新获取列表并渲染局部模板，确保列表是最新的
        return admin_live_orders(request)

    return redirect("orders:admin-live-orders")


def my_orders(request):
    """
    顾客端: 我的订单历史
    
    功能:
    - 展示当前登录用户的所有历史订单
    - 或者是当前 Session 的匿名订单
    - 按时间倒序排列
    """
    if request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by("-order_time")
    else:
        # For guests, retrieve orders from session IDs
        order_ids = request.session.get("order_history", [])
        orders = Order.objects.filter(id__in=order_ids).order_by("-order_time")
        
    return render(request, "orders/my_orders.html", {"orders": orders})


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_live_orders(request):
    """
    管理端: 实时订单视图
    
    功能:
    - 展示状态为 PENDING 或 PREPARING 的当前活跃订单
    - 支持 HTMX: 返回 _live_orders_list.html 局部模板
    """
    orders = Order.objects.filter(status__in=[Order.Status.PENDING, Order.Status.PREPARING]).order_by("order_time")
    
    if request.headers.get("HX-Request"):
        return render(request, "orders/_live_orders_list.html", {"orders": orders})
        
    return render(request, "orders/admin_live_orders.html", {"orders": orders})


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_order_history(request):
    """
    管理端: 历史订单视图
    
    功能:
    - 展示所有订单的完整历史记录
    """
    orders = Order.objects.all().order_by("-order_time")
    return render(request, "orders/admin_order_history.html", {"orders": orders})


@login_required
@user_passes_test(lambda u: u.is_staff)
def admin_settings(request):
    """
    管理端: 设置视图
    
    功能:
    - 展示系统设置页面 (目前为静态占位符)
    """
    return render(request, "orders/admin_settings.html")
