from django.db.models.signals import post_save, pre_delete, post_delete
from django.dispatch import receiver
from .models import Purchase

@receiver(post_save, sender=Purchase)
def purchase_post_save(sender, instance, created, **kwargs):
    """
    Signal handler for post-save events on Purchase model
    """
    if created:
        print(f"New purchase created: {instance.purchase_code} - {instance.product.name} by {instance.customer.get_full_name()}")
        
        # Update product stock if it's a new purchase
        if instance.product and instance.quantity:
            current_stock = instance.product.stock_quantity
            print(f"Product {instance.product.name} stock updated: {current_stock + instance.quantity} -> {current_stock}")

@receiver(pre_delete, sender=Purchase)
def purchase_pre_delete(sender, instance, **kwargs):
    """
    Signal handler for pre-delete events on Purchase model
    Restore product stock when purchase is deleted
    """
    if instance.product and instance.quantity:
        # This will be handled in the view, but we can log it here
        print(f"Purchase {instance.purchase_code} being deleted - stock will be restored")

@receiver(post_delete, sender=Purchase)
def purchase_post_delete(sender, instance, **kwargs):
    """
    Signal handler for post-delete events on Purchase model
    """
    print(f"Purchase {instance.purchase_code} has been deleted")