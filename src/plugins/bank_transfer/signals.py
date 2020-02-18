from django.dispatch import receiver

from core.signals import payment_method_forms

from .payment_method import BankTransfer


@receiver(payment_method_forms)
def payment_method_form(sender, **kwargs):
    return 'test'
