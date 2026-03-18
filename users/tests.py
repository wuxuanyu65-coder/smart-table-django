from django.test import TestCase
from django.contrib.auth import get_user_model
from menu.models import Allergen

User = get_user_model()

class UserModelTests(TestCase):
    def setUp(self):
        self.allergen1 = Allergen.objects.create(name="Peanut", category=Allergen.Category.NUTS)
        self.allergen2 = Allergen.objects.create(name="Milk", category=Allergen.Category.COMMON)
        
    def test_create_user_with_role(self):
        user = User.objects.create_user(
            username="testuser",
            password="testpassword123",
            role=User.Roles.CUSTOMER
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.role, "customer")
        self.assertTrue(user.check_password("testpassword123"))

    def test_user_string_representation(self):
        user = User.objects.create_user(
            username="staffuser",
            password="password",
            role=User.Roles.STAFF
        )
        self.assertEqual(str(user), "staffuser (staff)")

    def test_user_allergens(self):
        user = User.objects.create_user(
            username="allergenuser",
            password="password"
        )
        user.allergens.add(self.allergen1, self.allergen2)
        
        self.assertEqual(user.allergens.count(), 2)
        self.assertIn(self.allergen1, user.allergens.all())
        self.assertIn(self.allergen2, user.allergens.all())
