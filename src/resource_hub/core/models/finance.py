from django.db import models
from django.utils.translation import gettext_lazy as _

from ..fields import CurrencyField, PercentField
from ..utils import normalize_fraction
from .base import BaseModel, BaseStateMachine


class Payment(BaseStateMachine):
    # constants
    class STATE(BaseStateMachine.STATE):
        # active states
        # final states
        FAILED = 'fa'
        CANCELED = 'ca'
        REFUNDED = 'r'
        # pseudo final states
        FINALIZED = 'f'

    STATES = [
        *BaseStateMachine.STATES,
        (STATE.FINALIZED, _('finalized')),
        (STATE.FAILED, _('failed')),
        (STATE.CANCELED, _('canceled')),
        (STATE.REFUNDED, _('refunded')),
    ]

    STATE_GRAPH = {
        STATE.PENDING: {STATE.FINALIZED, STATE.CANCELED, STATE.FAILED},
        STATE.FINALIZED: {STATE.REFUNDED},
    }

    # fields
    debitor = models.ForeignKey(
        'Actor',
        on_delete=models.PROTECT,
        related_name='payment_debitor',
        verbose_name=_('Debitor'),
    )
    creditor = models.ForeignKey(
        'Actor',
        on_delete=models.PROTECT,
        related_name='payment_creditor',
        verbose_name=_('Creditor'),
    )
    value = models.DecimalField(
        decimal_places=5,
        max_digits=15,
        verbose_name=_('Value'),
    )
    currency = CurrencyField()
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Payment notes'),
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Payment date'),
    )
    payment_method = models.ForeignKey(
        'PaymentMethod',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Payment method'),
    )


class Price(BaseModel):
    addressee = models.ForeignKey(
        'Actor',
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
        verbose_name=_('Addressee'),
    )
    value = models.DecimalField(
        decimal_places=5,
        max_digits=15,
        verbose_name=_('Price'),
    )
    currency = CurrencyField()
    discounts = models.BooleanField(
        default=True,
        blank=True,
        verbose_name=_('Discounts'),
    )

    def __str__(self):
        return '{} {}'.format(normalize_fraction(self.value), self.currency)


class PriceProfile(BaseModel):
    contract_procedure = models.ForeignKey(
        'ContractProcedure',
        on_delete=models.PROTECT,
        verbose_name=_('Contract procedure'),
    )
    addressee = models.ForeignKey(
        'Actor',
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
        verbose_name=_('Addressee'),
    )
    description = models.CharField(
        max_length=64,
        verbose_name=_('Description'),
    )
    discount = PercentField(
        verbose_name=_('Discount'),
    )

    # methods
    def __str__(self):
        addressee = '' if self.addressee is None else '({})'.format(
            self.addressee.name)
        return '{}%: {} {}'.format(self.discount, self.description, addressee)

    def apply(self, net):
        return float(net) * (1 - (float(self.discount)/100))
