from collections import OrderedDict

from django import forms

from core.forms import BankAccountForm

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


class BankTransferFormManager():
    def __init__(self, POST=None):
        self.bank_transfer_form = BankTransferForm(POST)
        self.bank_account_form = BankAccountForm(POST)

    def get_form(self):
        result = OrderedDict()
        result.update(self.bank_transfer_form.fields.items())
        result.update(self.bank_account_form.fields.items())
        return result

    def is_valid(self):
        return (
            self.bank_transfer_form.is_valid() and
            self.bank_account_form.is_valid()
        )

    def get_errors(self):
        result = {}
        result.update(self.bank_transfer_form.errors)
        result.update(self.bank_account_form.errors)
        print(result)
        # return result
        # result = self.bank_transfer_form.errors.as_ul(
        # ) + self.bank_transfer_form.errors.as_ul()
        # print(result)
        return result

    def save(self, commit=True):
        new_bank_transfer = self.bank_transfer_form.save(commit=False)
        new_bank_account = self.bank_account_form.save()
        new_bank_transfer.bank_account = new_bank_account

        if commit:
            new_bank_transfer.save()

        return new_bank_transfer
