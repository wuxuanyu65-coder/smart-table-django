from decimal import Decimal
from django.test import TestCase
from .models import MenuItem, Favorite, Allergen
from orders.models import Order
from tables.models import Table
from users.models import User
from django.urls import reverse
from django.utils import timezone


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


class MenuManagementTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", password="password")
        self.client.force_login(self.admin)
        # Create some allergens
        self.nut = Allergen.objects.create(name="Nuts", category=Allergen.Category.NUTS)
        self.dairy = Allergen.objects.create(name="Dairy", category=Allergen.Category.COMMON)

    def test_add_menu_item_with_dietary_info(self):
        """Test adding a menu item with dietary info via the form view"""
        response = self.client.post(reverse("menu-add"), {
            "name": "New Dish",
            "description": "Tasty",
            "price": "12.50",
            "category": "Main",
            "is_available": "on",
            "allergens": [self.nut.id],
            "is_vegan": "on"
        })
        
        # Should redirect to manage page
        self.assertRedirects(response, reverse("menu-manage"))
        
        # Check if item created
        item = MenuItem.objects.get(name="New Dish")
        self.assertEqual(item.price, Decimal("12.50"))
        
        # Check dietary info
        self.assertTrue(item.is_vegan)
        self.assertIn(self.nut, item.allergens.all())

    def test_edit_menu_item_with_dietary_info(self):
        """Test editing a menu item and its dietary info"""
        item = MenuItem.objects.create(name="Old Dish", price=Decimal("10.00"), category="Main")
        item.allergens.add(self.nut)
        item.is_gluten_free = True
        item.save()
        
        response = self.client.post(reverse("menu-edit", args=[item.id]), {
            "name": "Updated Dish",
            "description": "Very Tasty",
            "price": "15.00",
            "category": "Main",
            "is_available": "on",
            "allergens": [self.dairy.id],
            "is_gluten_free": "on",
            "is_vegetarian": "on"
        })
        
        self.assertRedirects(response, reverse("menu-manage"))
        
        item.refresh_from_db()
        self.assertEqual(item.name, "Updated Dish")
        self.assertEqual(item.price, Decimal("15.00"))
        self.assertIn(self.dairy, item.allergens.all())
        self.assertNotIn(self.nut, item.allergens.all())
        self.assertTrue(item.is_gluten_free)
        self.assertTrue(item.is_vegetarian)


    def test_add_menu_item_view_context(self):
        """Test that the add menu item view context contains grouped allergens"""
        from .models import Allergen
        
        # Create allergens in different categories
        Allergen.objects.create(name="Peanuts", category=Allergen.Category.NUTS)
        Allergen.objects.create(name="Shrimp", category=Allergen.Category.SEAFOOD)
        Allergen.objects.create(name="Milk", category=Allergen.Category.COMMON)
        Allergen.objects.create(name="Unknown", category=Allergen.Category.OTHER)
        
        response = self.client.get(reverse("menu-add"))
        
        self.assertEqual(response.status_code, 200)
        self.assertIn("grouped_allergens", response.context)
        
        groups = response.context["grouped_allergens"]
        # Check keys match categories
        self.assertIn(Allergen.Category.NUTS, groups)
        self.assertIn(Allergen.Category.SEAFOOD, groups)
        self.assertIn(Allergen.Category.COMMON, groups)
        self.assertIn(Allergen.Category.OTHER, groups)
        
        # Check content
        # setUp creates 1 NUT allergen ("Nuts"), we added "Peanuts" -> Total 2
        nuts_widgets = groups[Allergen.Category.NUTS]['widgets']
        self.assertEqual(len(nuts_widgets), 2)
        
        # Check labels exist in the group
        labels = [w.data['label'] for w in nuts_widgets]
        self.assertIn("Peanuts", labels)
        self.assertIn("Nuts", labels)


class AdminDashboardTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser(username="admin", password="password")
        self.client.force_login(self.admin)
        self.table = Table.objects.create(table_number=1)

    def test_admin_dashboard_stats(self):
        """Test that the dashboard correctly calculates stats"""
        # Create orders
        # 1. Today, Pending
        Order.objects.create(table=self.table, status=Order.Status.PENDING, total_price=Decimal("10.00"))
        # 2. Today, Preparing
        Order.objects.create(table=self.table, status=Order.Status.PREPARING, total_price=Decimal("20.00"))
        # 3. Today, Completed
        Order.objects.create(table=self.table, status=Order.Status.COMPLETED, total_price=Decimal("30.00"))
        
        # 4. Old Order (Yesterday) - should not count towards today's revenue/count but check logic
        # Django auto-sets auto_now_add=True, so we need to hack it or just accept we test today's logic mostly
        # Actually, let's just test today's logic for now as mocking time is complex
        
        response = self.client.get(reverse("admin-dashboard"))
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["today_order_count"], 3)
        self.assertEqual(response.context["today_revenue"], Decimal("60.00"))
        self.assertEqual(response.context["pending_count"], 1)
        self.assertEqual(response.context["preparing_count"], 1)
