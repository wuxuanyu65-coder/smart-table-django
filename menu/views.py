from django.shortcuts import render
from .models import MenuItem


def menu_list(request):
    items = MenuItem.objects.filter(is_available=True).order_by("category", "name")
    categories = items.values_list("category", flat=True).distinct()
    return render(request, "menu/menu.html", {"items": items, "categories": categories})
