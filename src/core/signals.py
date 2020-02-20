from django.dispatch import Signal

register_payment_methods = Signal(
    providing_args=[],
)
