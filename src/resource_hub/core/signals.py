from django.dispatch import Signal

register_payment_methods = Signal(
    providing_args=[],
)

register_contract_procedures = Signal(
    providing_args=[],
)
