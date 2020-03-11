
from django.forms.models import model_to_dict

from resource_hub.core.forms import BankAccountForm
from resource_hub.core.models import BankAccount

from .models import BankTransfer


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
