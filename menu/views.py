from django.shortcuts import render
from .models import MenuItem


def menu_list(request):
    cat = request.GET.get("cat")
    base_qs = MenuItem.objects.filter(is_available=True)
    if cat:
        base_qs = base_qs.filter(category=cat)
    items = base_qs.order_by("name")

    cart = request.session.get("cart", {})
    if not isinstance(cart, dict):
        cart = {}
    qty_by_id = {int(k): v for k, v in cart.items() if str(k).isdigit() or isinstance(k, int)}
    for it in items:
        it.current_qty = qty_by_id.get(it.id, 0)

    # Distinct categories for filter chips (use full available set)
    categories = (
        MenuItem.objects.filter(is_available=True)
        .order_by("category")
        .values_list("category", flat=True)
        .distinct()
    )

    # HTMX partial: return only the grid items to swap into #menu-grid
    if request.headers.get("HX-Request") == "true":
        return render(request, "menu/_grid.html", {"items": items})

    return render(request, "menu/menu.html", {"items": items, "categories": categories})
