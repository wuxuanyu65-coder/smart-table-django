from django.core.management.base import BaseCommand
from menu.models import MenuItem


class Command(BaseCommand):
    help = "Seed demo menu items for SmartTable"

    def handle(self, *args, **options):
        data = [
            {"name": "Tomato Soup", "description": "Classic tomato soup", "price": 9, "category": "Starters"},
            {"name": "Black Pepper Beef Pasta", "description": "", "price": 15, "category": "Mains"},
            {"name": "Americano", "description": "", "price": 6, "category": "Drinks"},
            {"name": "Latte", "description": "", "price": 6, "category": "Drinks"},
        ]
        created = 0
        for item in data:
            obj, was_created = MenuItem.objects.get_or_create(
                name=item["name"],
                defaults={
                    "description": item["description"],
                    "price": item["price"],
                    "category": item["category"],
                    "is_available": True,
                },
            )
            created += 1 if was_created else 0
        self.stdout.write(self.style.SUCCESS(f"Seed complete. New items: {created}"))

