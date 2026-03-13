from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Roles(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        STAFF = "staff", "Staff"
        MANAGER = "manager", "Manager"

    role = models.CharField(max_length=16, choices=Roles.choices, default=Roles.CUSTOMER)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.username} ({self.role})"

