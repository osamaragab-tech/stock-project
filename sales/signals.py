from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SaleItem
from inventory.models import StockMovement

@receiver(post_save, sender=SaleItem)
def update_inventory_on_sale(sender, instance, created, **kwargs):
    if created:
        product = instance.product
        product.quantity -= instance.quantity
        product.save()

        StockMovement.objects.create(
            product=product,
            quantity=instance.quantity,
            movement_type='out',
            description=f"Sale #{instance.sale.id}"
        )
