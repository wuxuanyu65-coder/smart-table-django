from django.shortcuts import render
from .models import MenuItem


def menu_list(request):
    items = MenuItem.objects.filter(is_available=True).order_by("category", "name")
    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    qty_by_id = {int(k): v for k, v in cart.items() if str(k).isdigit() or isinstance(k, int)}
    for it in items:
        it.current_qty = qty_by_id.get(it.id, 0)
    categories = items.values_list("category", flat=True).distinct()
    return render(request, "menu/menu.html", {"items": items, "categories": categories})
