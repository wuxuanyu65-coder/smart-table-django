from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:item_id>/", views.cart_add, name="cart-add"),
    path("cart/dec/<int:item_id>/", views.cart_dec, name="cart-dec"),
    path("checkout/", views.checkout, name="checkout"),
    path("success/<int:order_id>/", views.order_success, name="order-success"),
]

