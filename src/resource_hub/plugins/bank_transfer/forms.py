from collections import OrderedDict

from django import forms

from resource_hub.core.forms import BankAccountForm

from .models import BankTransfer


class BankTransferForm(forms.ModelForm):
    class Meta:
        model = BankTransfer
        fields = ['name', 'comment', 'bank_account',
                  'fee_absolute', 'fee_value']

    def save(self, request=None, commit=True, *args, **kwargs):
        new_bank_transfer = super(BankTransferForm, self).save(
            commit=False, *args, **kwargs)
        new_bank_transfer.owner = request.actor
        if commit:
            new_bank_transfer.save()
        return new_bank_transfer
