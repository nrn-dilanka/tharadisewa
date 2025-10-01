from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import Product
import os

@receiver(post_save, sender=Product)
def product_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for post-save events on Product model
    """
    if created:
        print(f"New product created: {instance.name}")

@receiver(pre_delete, sender=Product)
def product_pre_delete(sender, instance, **kwargs):
    """
    Signal handler for pre-delete events on Product model
    Clean up QR code file when product is deleted
    """
    if instance.qr_code:
        # Delete the QR code file from storage
        if os.path.isfile(instance.qr_code.path):
            os.remove(instance.qr_code.path)
        print(f"QR code file deleted for product: {instance.name}")