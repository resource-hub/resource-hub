from django.contrib import messages
from django.db import models, transaction
from django.db.models import Sum
from django.shortcuts import redirect, reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from resource_hub.core.models import BankAccount, Payment, PaymentMethod


class Cash(PaymentMethod):

    # attributes
    @property
    def verbose_name(self) -> str:
        return _('Cash')

    @property
    def info(self) -> dict:
        return {
            'name': self.verbose_name,
            'provider': 'Resource Hub Team',
            'description': _('The other party gets the necessary information to pay via direct bank transfer'),
            'thumbnail': 'images/default.png',
        }

    @property
    def form(self):
        from .forms import CashForm
        return CashForm

    @property
    def prefix(self) -> str:
        return 'csh'

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
            'The invoice has been settled in cash'
        )
