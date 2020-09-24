import re

from django import forms
from django.forms.models import model_to_dict
from django.utils.translation import gettext_lazy as _

from resource_hub.core.forms import BankAccountForm
from resource_hub.core.models import BankAccount

from .models import SEPA, SEPADirectDebitXML
from .settings import SCHEMA


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

    def clean_creditor_id(self):
        ''' use regex from schema pain.008.003.02 '''
        creditor_id = self.cleaned_data['creditor_id']
        if re.match(r"[a-zA-Z]{2,2}[0-9]{2,2}([A-Za-z0-9]|[\\+|\\?|/|\\-|:|\\(|\\)|\\.|,|']){3,3}([A-Za-z0-9]|[\\+|\\?|/|\\-|:|\\(|\\)|\\.|,|']){1,28}", creditor_id):
            return creditor_id
        raise forms.ValidationError(
            _('Not a valid creditor ID. Please refer to %(schema)s') % {'schema': SCHEMA}, code='invalid-creditor-id')

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
