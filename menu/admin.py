from django.contrib import admin
from .models import MenuItem, DietaryInfo, Favorite


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "category", "price", "is_available")
    search_fields = ("name", "category")
    list_filter = ("category", "is_available")


@admin.register(DietaryInfo)
class DietaryInfoAdmin(admin.ModelAdmin):
    list_display = ("id", "menu_item", "dietary_tags")


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "item", "created_at")
    search_fields = ("user__username", "item__name")

