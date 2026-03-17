from django.conf import settings
from django.db import models
from tables.models import Table
from menu.models import MenuItem


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PREPARING = "preparing", "Preparing"
        READY = "ready", "Ready"
        COMPLETED = "completed", "Completed"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    table = models.ForeignKey(Table, on_delete=models.PROTECT, related_name="orders")
    order_time = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    note = models.TextField(blank=True, null=True, help_text="Order-level notes (e.g. allergies, special requests)")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)

    def __str__(self) -> str:
        return f"Order #{self.id} - {self.table} - {self.status}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(MenuItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    special_request = models.CharField(max_length=255, blank=True)

    def line_total(self) -> float:
        return float(self.quantity) * float(self.price)

    def __str__(self) -> str:
        return f"{self.item.name} x{self.quantity}"

