from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("users.urls")),
    path("menu/", include("menu.urls")),
    path("orders/", include("orders.urls")),
    path("tables/", include("tables.urls")),
    path("", RedirectView.as_view(pattern_name="menu", permanent=False)),
]

