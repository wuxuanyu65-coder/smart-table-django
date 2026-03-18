from django.test import TestCase
from django.db.utils import IntegrityError
from .models import Table

class TableModelTests(TestCase):
    def test_create_table(self):
        table = Table.objects.create(table_number=5, qr_code_url="http://example.com/qr/5")
        self.assertEqual(table.table_number, 5)
        self.assertEqual(table.qr_code_url, "http://example.com/qr/5")
        
    def test_table_str_representation(self):
        table = Table.objects.create(table_number=10)
        self.assertEqual(str(table), "Table 10")
        
    def test_table_number_unique(self):
        Table.objects.create(table_number=1)
        with self.assertRaises(IntegrityError):
            Table.objects.create(table_number=1)
