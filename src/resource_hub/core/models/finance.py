import string
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.core.files.base import ContentFile
from django.db import DatabaseError, models, transaction
from django.db.models import Max, Min
from django.db.models.functions import Cast
from django.http import HttpResponse
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import pgettext
from django.utils.translation import gettext_lazy as _

import pycountry
from django_countries.fields import CountryField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from ipware import get_client_ip
from model_utils.fields import MonitorField
from model_utils.managers import InheritanceManager

from ..fields import CurrencyField, PercentField
from ..renderer import InvoiceRenderer
from ..settings import COUNTRIES_WITH_STATE_IN_ADDRESS
from ..utils import get_valid_slug, language
from .base import BaseModel


class Payment(BaseModel):
    # constants
    class STATE:
        # active states
        INIT = 'i'
        PENDING = 'p'
        # final states
        FAILED = 'fa'
        CANCELED = 'ca'
        REFUNDED = 'r'
        # pseudo final states
        FINALIZED = 'f'

    STATES = [
        (STATE.INIT, _('initializing')),
        (STATE.PENDING, _('pending')),
        (STATE.FINALIZED, _('finalized')),
        (STATE.FAILED, _('failed')),
        (STATE.CANCELED, _('canceled')),
        (STATE.REFUNDED, _('refunded')),
    ]

    STATE_GRAPH = {
        STATE.INIT: {STATE.PENDING},
        STATE.PENDING: {STATE.FINALIZED, STATE.CANCELED, STATE.FAILED},
        STATE.FINALIZED: {STATE.REFUNDED},
    }

    # fields
    state = models.CharField(
        choices=STATES,
        max_length=2,
        default=STATE.INIT,
    )
    state_changed = MonitorField(monitor='state')
    debitor = models.ForeignKey(
        'Actor',
        on_delete=models.PROTECT,
        related_name='payment_debitor',
    )
    creditor = models.ForeignKey(
        'Actor',
        on_delete=models.PROTECT,
        related_name='payment_creditor',
    )
    value = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    currency = CurrencyField()
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('payment notes'),
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
    )
    payment_method = models.ForeignKey(
        'PaymentMethod',
        null=True,
        on_delete=models.SET_NULL,
    )


class Price(models.Model):
    addressee = models.ForeignKey(
        'Actor',
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
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
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return '{} {}'.format(self.value.normalize(), self.currency)


class PriceProfile(models.Model):
    contract_procedure = models.ForeignKey(
        'ContractProcedure',
        on_delete=models.PROTECT,
    )
    addressee = models.ForeignKey(
        'Actor',
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE
    )
    description = models.CharField(
        max_length=64,
    )
    discount = PercentField()

    # methods
    def __str__(self):
        addressee = '' if self.addressee is None else '({})'.format(
            self.addressee.name)
        return '{}%: {} {}'.format(self.discount, self.description, addressee)

    def apply(self, net):
        return float(net) * (1 - (float(self.discount)/100))
