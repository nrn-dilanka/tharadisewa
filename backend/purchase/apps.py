from django.apps import AppConfig


class PurchaseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "purchase"
    verbose_name = "Purchase Management"
    
    def ready(self):
        """
        Import signals when the app is ready
        """
        try:
            import purchase.signals
        except ImportError:
            pass
