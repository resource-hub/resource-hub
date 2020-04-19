from django import forms
from django.forms.models import model_to_dict

from resource_hub.core.forms import BankAccountForm
from resource_hub.core.models import BankAccount

from .models import SEPA, SEPADirectDebitXML


class SEPAForm(BankAccountForm):
    # hacky way to make multi model form inheritance work
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        self.has_instance = False
        if instance is None:
            super(SEPAForm, self).__init__(*args, **kwargs)
        else:
            bank_account = model_to_dict(instance.bank_account)
            self.has_instance = True
            super(SEPAForm, self).__init__(
                *args, initial=bank_account, **kwargs)

    class Meta:
        model = SEPA
        fields = ['name', 'comment', 'creditor_id', 'is_prepayment', 'account_holder', 'iban', 'bic',
                  'currency', 'fee_absolute_value', 'fee_relative_value', 'fee_tax_rate', ]

    def save(self, request=None, commit=True):
        new_sepa = super(SEPAForm, self).save(
            commit=False)
        bank_account = {
            'account_holder': self.cleaned_data['account_holder'],
            'iban': self.cleaned_data['iban'],
            'bic': self.cleaned_data['bic'],
        }
        if self.has_instance:
            BankAccount.objects.filter(
                pk=self.instance.bank_account.pk).update(**bank_account)
        else:
            new_sepa.bank_account = BankAccount.objects.create(
                **bank_account)
        new_sepa.owner = request.actor

        if commit:
            new_sepa.save()
        return new_sepa


class SEPADirectDebitXMLForm(forms.ModelForm):
    class Meta:
        model = SEPADirectDebitXML
        fields = ['batch', 'collection_date']
