from django.urls import path
from . import views

urlpatterns = [
    path("", views.menu_list, name="menu"),
    path("manage/", views.menu_manage, name="menu-manage"),
    path("add/", views.add_menu_item, name="menu-add"),
    path("edit/<int:pk>/", views.edit_menu_item, name="menu-edit"),
    path("delete/<int:pk>/", views.delete_menu_item, name="menu-delete"),
    path("favorite/<int:item_id>/", views.toggle_favorite, name="toggle-favorite"),
    path("favorites/", views.favorites_list, name="favorites-list"),
    path("manage/add-allergen/", views.add_allergen, name="add-allergen"),
]
