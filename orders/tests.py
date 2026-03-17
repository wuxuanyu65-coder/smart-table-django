from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Order, OrderItem
from menu.models import MenuItem
from tables.models import Table

User = get_user_model()

class OrderCheckoutTests(TestCase):
    def setUp(self):
        # Create test data
        self.user = User.objects.create_user(username="testuser", password="password")
        self.client = Client()
        self.client.force_login(self.user)
        
        self.table = Table.objects.create(table_number="1")
        self.item = MenuItem.objects.create(name="Burger", price=10.00, category="Mains")
        
        # Add item to cart session
        session = self.client.session
        session["cart"] = {str(self.item.id): 2}
        session["table_id"] = "1"
        session.save()

    def test_checkout_creates_order(self):
        url = reverse("orders:checkout")
        response = self.client.post(url, {f"note_{self.item.id}": "No onions"})
        
        self.assertEqual(response.status_code, 302)  # Redirects to success
        
        # Verify Order created
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.table, self.table)
        self.assertEqual(order.total_price, 20.00)
        
        # Verify OrderItem created with note
        order_item = OrderItem.objects.first()
        self.assertEqual(order_item.item, self.item)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, self.item.price) # Verify price freeze
        self.assertEqual(order_item.special_request, "No onions")

class AdminPermissionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="normal", password="password")
        self.admin = User.objects.create_user(username="staff", password="password", is_staff=True)
        self.client = Client()

    def test_admin_view_requires_staff(self):
        url = reverse("orders:admin-live-orders")
        
        # Case 1: Not logged in
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 200) # Should redirect
        
        # Case 2: Normal user
        self.client.force_login(self.user)
        resp = self.client.get(url)
        self.assertNotEqual(resp.status_code, 200) # Should redirect/forbidden
        
        # Case 3: Staff user
        self.client.force_login(self.admin)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)