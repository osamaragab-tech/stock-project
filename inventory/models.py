from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from products.models import Product

# ==========================
# 3️⃣ حركة المخزون (Stock Movement)
# ==========================
class StockMovement(models.Model):
    MOVEMENT_TYPES = [
        ('in', _('Stock In')),
        ('out', _('Stock Out')),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    movement_type = models.CharField(max_length=10, choices=MOVEMENT_TYPES)
    date = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.movement_type} ({self.quantity})"


# ==========================
# 4️⃣ المعاملات (Transactions)
# ==========================
class Transaction(models.Model):
    OPERATION_CHOICES = [
        ('IN', _('Stock In')),
        ('OUT', _('Stock Out')),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='transactions')
    quantity = models.PositiveIntegerField(default=0)
    operation = models.CharField(max_length=3, choices=OPERATION_CHOICES)
    date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} - {self.operation} ({self.quantity})"
