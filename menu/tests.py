from decimal import Decimal
from django.test import TestCase
from .models import MenuItem, Favorite
from users.models import User


class MenuModelTests(TestCase):
    def test_menu_item_str(self):
        it = MenuItem.objects.create(name="Soup", description="", price=Decimal("3.00"), category="Starter")
        self.assertIn("Soup", str(it))

    def test_favorite_unique(self):
        it = MenuItem.objects.create(name="Soup", description="", price=Decimal("3.00"), category="Starter")
        u = User.objects.create_user(username="alice", password="p")
        Favorite.objects.create(user=u, item=it)
        with self.assertRaises(Exception):
            Favorite.objects.create(user=u, item=it)
