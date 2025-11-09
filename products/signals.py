from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Product

@receiver(post_save, sender=Product)
def set_initial_stock(sender, instance, created, **kwargs):
    if created and instance.beginning_balance > 0:
        instance.quantity = instance.beginning_balance
        instance.save()
