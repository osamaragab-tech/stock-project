from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _
import random

class Category(models.Model):
        name = models.CharField(max_length=100,  verbose_name=_("Category Name"))
        parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='subcategories',
        verbose_name=_("Parent Category")
        )


        def __str__(self):
            return f"{self.parent.name} > {self.name}" if self.parent else self.name




class Product(models.Model):
    PRODUCT_TYPES = [
        ('inventory', _('Inventory Item')),
        ('notinventory', _('Non-Inventory Item')),
        ('service', _('Service')),
    ]

    name = models.CharField(max_length=150, unique=True, verbose_name=_("Product Name"))
    sku = models.CharField(max_length=100, unique=True, verbose_name=_("SKU"))
    barcode = models.CharField(max_length=100, unique=True, blank=True, null=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True)
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPES, default='inventory')
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    beginning_balance = models.PositiveIntegerField(default=0)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.name

    @property
    def on_hand(self):
        """✅ الرصيد الفعلي من تطبيق المخزون"""
        try:
            from inventory.models import StockMovement
            ins = self.stockmovement_set.filter(movement_type='in').aggregate(models.Sum('quantity'))['quantity__sum'] or 0
            outs = self.stockmovement_set.filter(movement_type='out').aggregate(models.Sum('quantity'))['quantity__sum'] or 0
            return ins - outs
        except Exception:
            return self.beginning_balance

    @property
    def total_value(self):
        try:
            return float(self.price) * (self.on_hand or 0)
        except Exception:
            return 0.0

    # ========================
    # 🔢 توليد باركود EAN-13
    # ========================
    def _generate_ean13(self):
        """ينشئ باركود صالح بصيغة EAN-13"""
        base = ''.join([str(random.randint(0, 9)) for _ in range(12)])
        total = sum((3 if i % 2 else 1) * int(n) for i, n in enumerate(base))
        check_digit = (10 - (total % 10)) % 10
        return f"{base}{check_digit}"

    def save(self, *args, **kwargs):
        """يحفظ المنتج مع توليد باركود تلقائي لو غير موجود"""
        if not self.barcode:
            self.barcode = self._generate_ean13()
        super().save(*args, **kwargs)