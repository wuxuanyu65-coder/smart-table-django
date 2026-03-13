from django.db import models


class Table(models.Model):
    table_number = models.PositiveIntegerField(unique=True)
    qr_code_url = models.URLField(blank=True, null=True)

    def __str__(self) -> str:
        return f"Table {self.table_number}"

