from django.apps import AppConfig


class ProductConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "product"
    verbose_name = "Product Management"
    
    def ready(self):
        """
        Import signals when the app is ready
        """
        try:
            import product.signals
        except ImportError:
            pass
