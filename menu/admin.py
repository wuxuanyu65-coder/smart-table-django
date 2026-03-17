from django.contrib import admin
from .models import MenuItem, Favorite


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "is_available", "is_vegetarian", "is_vegan", "is_gluten_free")
    search_fields = ("name", "category")
    list_filter = ("category", "is_available", "is_vegetarian", "is_vegan", "is_gluten_free")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "item", "created_at")
    search_fields = ("user__username", "item__name")

