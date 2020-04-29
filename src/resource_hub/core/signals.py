from django.dispatch import Signal, receiver

from .modules import CoreModule

register_payment_methods = Signal(
    providing_args=[],
)

register_contract_procedures = Signal(
    providing_args=[],
)

control_sidebar_finance = Signal(
    providing_args=[],
)
register_modules = Signal(
    providing_args=[],
)


@receiver(register_modules)
def register_module(sender, **kwargs):
    return CoreModule
