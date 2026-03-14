from decimal import Decimal
from django.test import TestCase
from menu.models import MenuItem
from tables.models import Table
from .models import Order, OrderItem


class OrderItemTests(TestCase):
    def test_line_total(self):
        item = MenuItem.objects.create(name="Test", description="", price=Decimal("2.50"), category="Test")
        table = Table.objects.create(table_number=1)
        order = Order.objects.create(table=table)
        oi = OrderItem.objects.create(order=order, item=item, quantity=3)
        self.assertEqual(oi.line_total(), 7.5)
