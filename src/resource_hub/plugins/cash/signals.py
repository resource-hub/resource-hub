from django.dispatch import receiver
from resource_hub.core.signals import register_payment_methods

from .models import Cash


@receiver(register_payment_methods)
def register_payment_method(sender, **kwargs):
    return Cash()
