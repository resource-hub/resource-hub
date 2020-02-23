from collections import OrderedDict

from django import forms

from resource_hub.core.models import BankAccount
from schwifty import BIC, IBAN

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
