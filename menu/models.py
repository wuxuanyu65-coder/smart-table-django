from django.conf import settings
from django.db import models


class Allergen(models.Model):
    class Category(models.TextChoices):
        COMMON = "common", "Common Allergens"
        SEAFOOD = "seafood", "Seafood"
        NUTS = "nuts", "Nuts & Seeds"
        OTHER = "other", "Other"

    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    
    def __str__(self) -> str:
        return self.name


class MenuItem(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.CharField(max_length=50)
    image = models.ImageField(upload_to="menu_images/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    
    # Dietary Flags
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    
    # Allergens (Replaced JSONField with ManyToManyField)
    allergens = models.ManyToManyField(Allergen, blank=True, related_name="menu_items")

    def __str__(self) -> str:
        return f"{self.name} - {self.price}"


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="favorites")
    item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name="favorited_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "item")

    def __str__(self) -> str:
        return f"{self.user} -> {self.item}"
