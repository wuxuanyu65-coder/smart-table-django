from django.urls import path
from . import views

urlpatterns = [
    path("", views.menu_list, name="menu"),
    path("dashboard/", views.admin_dashboard, name="admin-dashboard"),
    path("manage/", views.menu_manage, name="menu-manage"),
    path("add/", views.add_menu_item, name="menu-add"),
    path("edit/<int:pk>/", views.edit_menu_item, name="menu-edit"),
    path("delete/<int:pk>/", views.delete_menu_item, name="menu-delete"),
]
