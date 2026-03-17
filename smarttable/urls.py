from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from menu import views as menu_views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("admin-dashboard/", menu_views.admin_dashboard, name="admin-dashboard"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("accounts/", include("users.urls")),
    path("profile/", include("users.profile_urls")), # Add dedicated profile URLs
    path("menu/", include("menu.urls")),
    path("orders/", include("orders.urls")),
    path("tables/", include("tables.urls")),
    path("", RedirectView.as_view(pattern_name="login", permanent=False)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
