
from django.forms.models import model_to_dict

from resource_hub.core.forms import BankAccountForm
from resource_hub.core.models import BankAccount

from .models import BankTransfer


class BankTransferForm(BankAccountForm):
    # hacky way to make multi model form inheritance work
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        self.has_instance = False
        if instance is None:
            super(BankTransferForm, self).__init__(*args, **kwargs)
        else:
            bank_account = model_to_dict(instance.bank_account)
            self.has_instance = True
            super(BankTransferForm, self).__init__(
                *args, initial=bank_account, **kwargs)

    class Meta:
        model = BankTransfer
        fields = ['name', 'comment', 'account_holder', 'iban', 'bic',
                  'fee_absolute', 'fee_value']

    def save(self, request=None, commit=True):
        new_bank_transfer = super(BankTransferForm, self).save(
            commit=False)
        bank_account = {
            'account_holder': self.cleaned_data['account_holder'],
            'iban': self.cleaned_data['iban'],
            'bic': self.cleaned_data['bic'],
        }
        if self.has_instance:
            new_bank_transfer.bank_account = BankAccount.objects.create(
                **bank_account)
        else:
            BankAccount.objects.filter(
                pk=self.instance.bank_account.pk).update(**bank_account)
        new_bank_transfer.owner = request.actor

        if commit:
            new_bank_transfer.save()
        return new_bank_transfer
