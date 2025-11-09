from django.db import models, transaction
from django.utils import timezone
from products.models import Product
from django.contrib.auth import get_user_model

User = get_user_model()

class Sale(models.Model):
    customer_name = models.CharField(max_length=200, blank=True, null=True)
    date = models.DateTimeField(default=timezone.now)
    total_amount = models.FloatField(default=0)

    def __str__(self):
        return f"Invoice #{self.id or 'New'} - {self.customer_name or 'Unknown'}"

    def update_total(self):
        """Recalculate total amount from all items."""
        total = sum(item.subtotal for item in self.items.all())
        self.total_amount = total
        self.save()


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        # احسب الإجمالي الفرعي فقط
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)

        # تحديث الإجمالي الكلي للفاتورة
        self.sale.update_total()

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


class SaleReturn(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.SET_NULL, null=True, blank=True, related_name='returns')
    date = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sale Return #{self.id} - {self.sale_id or 'No Sale'}"


class SaleReturnItem(models.Model):
    sale_return = models.ForeignKey(SaleReturn, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    price = models.FloatField(default=0)
    subtotal = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantity * self.price
        super().save(*args, **kwargs)