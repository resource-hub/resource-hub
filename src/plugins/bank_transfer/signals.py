from django.dispatch import receiver

from core.signals import register_payment_methods

from .forms import BankTransferForm
from .models import BankTransfer


@receiver(register_payment_methods)
def register_payment_method(sender, **kwargs):
    return BankTransfer
