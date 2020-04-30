from django.contrib import messages
from django.db import models, transaction
from django.db.models import Sum
from django.shortcuts import redirect, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from resource_hub.core.models import BankAccount, Payment, PaymentMethod


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
        total = claims.aggregate(total=Sum('gross'))['total']
        Payment.objects.create(
            payment_method=self,
            state=Payment.STATE.FINALIZED,
            creditor=contract.creditor,
            debitor=contract.debitor,
            value=total,
            payment_date=timezone.now(),
        )

    def get_invoice_text(self) -> str:
        return _(
            'Please make a SEPA credit transfer of the above mentioned gross amount to the following account: \n {account_holder} \n {iban} \n {bic}'.format(
                account_holder=self.bank_account.account_holder,
                iban=self.bank_account.iban,
                bic=self.bank_account.bic
            )
        )
