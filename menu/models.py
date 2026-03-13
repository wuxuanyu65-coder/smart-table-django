from django.conf import settings
from django.db import models


class MenuItem(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=50)
    is_available = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.name} - {self.price}"


class DietaryInfo(models.Model):
    menu_item = models.OneToOneField(MenuItem, on_delete=models.CASCADE, related_name="dietary_info")
    allergen_info = models.TextField(blank=True)
    dietary_tags = models.CharField(max_length=255, blank=True)

    def __str__(self) -> str:
        return f"DietaryInfo for {self.menu_item.name}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "item")

    def __str__(self) -> str:
        return f"{self.user} -> {self.item}"

