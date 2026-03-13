from django.contrib import admin
from .models import Table


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ("id", "table_number", "qr_code_url")
    search_fields = ("table_number",)

