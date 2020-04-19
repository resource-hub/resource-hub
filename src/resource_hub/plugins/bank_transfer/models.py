from django.contrib import messages
from django.db import models, transaction
from django.shortcuts import redirect, reverse
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
    def prefix(self) -> str:
        return 'bnk'

    def initialize(self, contract, request):
        if not self.is_prepayment:
            raise ValueError(
                'payment method can only initialized if it is a prepayment')
        with transaction.atomic():
            contract.set_waiting(request)
        message = _('%(name)s has been confirmed successfully') % {
            'name': contract.verbose_name}
        messages.add_message(request, messages.SUCCESS, message)
        return redirect(reverse('control:finance_contracts_manage_details', kwargs={'pk': contract.pk}))

    def settle(self, contract, claims, invoice):
        pass
