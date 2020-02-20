from collections import OrderedDict

from django.db import models
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from core.models import BankAccount, PaymentMethod


class BankTransfer(PaymentMethod):
    # fields
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
    )

    # attributes
    @staticmethod
    def verbose_name() -> str:
        return _('Bank transfer')

    @staticmethod
    def info() -> dict:
        return {
            'name': BankTransfer.verbose_name(),
            'provider': 'Resource Hub Team',
            'description': _('The other party gets the necessary information to pay via direct bank transfer'),
            'thumbnail': 'images/default.png',
        }

    @staticmethod
    def form() -> OrderedDict:
        from .forms import BankTransferForm
        return BankTransferForm

    @staticmethod
    def form_url() -> str:
        return reverse('control:bank_transfer_create')

    @staticmethod
    def prefix() -> str:
        return 'bnk'

    # methods
    def callback(self):
        return
