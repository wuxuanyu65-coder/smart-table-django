from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:item_id>/", views.cart_add, name="cart-add"),
    path("cart/dec/<int:item_id>/", views.cart_dec, name="cart-dec"),
    path("checkout/confirm/", views.checkout_confirmation, name="checkout-confirmation"),
    path("checkout/", views.checkout, name="checkout"),
    path("success/<int:order_id>/", views.order_success, name="order-success"),
    path("my-orders/", views.my_orders, name="my-orders"),
    path("manage/live/", views.admin_live_orders, name="admin-live-orders"),
    path("manage/history/", views.admin_order_history, name="admin-order-history"),
    path("manage/settings/", views.admin_settings, name="admin-settings"),
    path("manage/update-status/<int:order_id>/", views.update_order_status, name="update-order-status"),
]

