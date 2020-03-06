from collections import OrderedDict

from django import forms
from django.forms.models import model_to_dict

from resource_hub.core.forms import BankAccountForm
from resource_hub.core.models import BankAccount

from .models import BankTransfer

# from resource_hub.core.forms import BankAccountForm


# class BankAccountForm(forms.Form):
#     account_holder = forms.CharField(max_length=100)
#     iban = forms.CharField(max_length=50)
#     bic = forms.CharField(max_length=10)

#     def clean_iban(self):
#         iban = self.cleaned_data['iban']
#         if iban:
#             try:
#                 IBAN(iban)
#             except ValueError as e:
#                 raise forms.ValidationError(
#                     _('Invalid IBAN: ') + str(e), code='invalid-iban')
#         return iban

#     def clean_bic(self):
#         bic = self.cleaned_data['bic']
#         if bic:
#             try:
#                 BIC(bic)
#             except ValueError as e:
#                 raise forms.ValidationError(
#                     _('Invalid BIC: ') + str(e), code='invalid-bic')
#         return bic

#     def save(self, commit=True):
#         new_bank_account = BankAccount.objects.create(
#             account_holder=self.cleaned_data['account_holder'],
#             iban=self.cleaned_data['iban'],
#             bic=self.cleaned_data['bic'],
#         )


class BankTransferForm(BankAccountForm):
    # hacky way to make multi model form inheritance work
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if instance is None:
            super(BankTransferForm, self).__init__(*args, **kwargs)
        else:
            initial = model_to_dict(instance.bank_account)
            super(BankTransferForm, self).__init__(
                *args, initial=initial, **kwargs)

    class Meta:
        model = BankTransfer
        fields = ['name', 'comment', 'account_holder', 'iban', 'bic',
                  'fee_absolute', 'fee_value']

    def save(self, request=None, commit=True, *args, **kwargs):
        new_bank_transfer = super(BankTransferForm, self).save(
            commit=False, *args, **kwargs)
        new_bank_transfer.bank_account = BankAccount.objects.create(
            account_holder=self.cleaned_data['account_holder'],
            iban=self.cleaned_data['iban'],
            bic=self.cleaned_data['bic'],
        )
        new_bank_transfer.owner = request.actor
        if commit:
            new_bank_transfer.save()
        return new_bank_transfer
