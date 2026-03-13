from decimal import Decimal
from typing import Dict
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST
from menu.models import MenuItem
from tables.models import Table
from .models import Order, OrderItem


def _get_cart(session) -> Dict[str, int]:
    cart = session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    return cart


def _cart_count(cart: Dict[str, int]) -> int:
    return sum(cart.values())


@require_POST
def cart_add(request: HttpRequest, item_id: int) -> HttpResponse:
    cart = _get_cart(request.session)
    key = str(item_id)
    cart[key] = cart.get(key, 0) + 1
    request.session["cart"] = cart
    count = _cart_count(cart)
    return HttpResponse(f'<span id="cart-count" hx-swap-oob="true">{count}</span>')


@require_POST
def cart_dec(request: HttpRequest, item_id: int) -> HttpResponse:
    cart = _get_cart(request.session)
    key = str(item_id)
    if key in cart:
        cart[key] = max(0, cart[key] - 1)
        if cart[key] == 0:
            del cart[key]
    request.session["cart"] = cart
    count = _cart_count(cart)
    return HttpResponse(f'<span id="cart-count" hx-swap-oob="true">{count}</span>')


def cart_view(request: HttpRequest) -> HttpResponse:
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
def checkout(request: HttpRequest) -> HttpResponse:
    cart = _get_cart(request.session)
    if not cart:
        return redirect("orders:cart")
    table, _ = Table.objects.get_or_create(table_number=1)
    order = Order.objects.create(table=table, status=Order.Status.PENDING, total_price=0)
    total = Decimal("0.00")
    for item_id, qty in cart.items():
        try:
            item = MenuItem.objects.get(id=int(item_id))
        except MenuItem.DoesNotExist:
            continue
        OrderItem.objects.create(order=order, item=item, quantity=qty)
        total += item.price * qty
    order.total_price = total
    order.save(update_fields=["total_price"])
    request.session["cart"] = {}
    return redirect(reverse("orders:order-success", args=[order.id]))


def order_success(request: HttpRequest, order_id: int) -> HttpResponse:
    return render(request, "orders/order_success.html", {"order_id": order_id})
