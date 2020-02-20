from django.contrib import messages
from django.shortcuts import redirect, reverse
from django.utils.translation import ugettext_lazy as _
from django.views import View

from .forms import BankTransferFormManager
from .models import BankTransfer


class BankTransferCreate(View):
    def post(self, request):
        bank_transfer_form = BankTransferFormManager()
        if bank_transfer_form.is_valid():
            bank_transfer_form.save()
            message = _('The bank transfer configuration has been saved')
            messages.add_message(request, messages.SUCCESS, message)

            return redirect(BankTransfer.redirect_route())

        message = _(bank_transfer_form.get_errors())
        messages.add_message(request, messages.ERROR, message)
        return (redirect(reverse('control:finance_payment_methods_add')))
