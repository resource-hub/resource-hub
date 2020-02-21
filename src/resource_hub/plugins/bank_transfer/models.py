from collections import OrderedDict

from django.db import models
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from resource_hub.core.models import BankAccount, PaymentMethod


class BankTransfer(PaymentMethod):
    # fields
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
    )

    # attributes
    @property
    def verbose_name(self) -> str:
        return _('Bank transfer')

    @property
    def edit_url(self):
        return reverse('control:bank_transfer_edit', kwargs={'pk': self.pk})

    @property
    def info(self) -> dict:
        return {
            'name': BankTransfer.verbose_name,
            'provider': 'Resource Hub Team',
            'description': _('The other party gets the necessary information to pay via direct bank transfer'),
            'thumbnail': 'images/default.png',
        }

    @property
    def form(self):
        from .forms import BankTransferForm
        return BankTransferForm

    @property
    def form_url(self) -> str:
        return reverse('control:bank_transfer_create')

    @property
    def prefix(self) -> str:
        return 'bnk'

    # methods
    def callback(self):
        return
