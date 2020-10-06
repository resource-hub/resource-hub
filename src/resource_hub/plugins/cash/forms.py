
from django import forms

from .models import Cash


class CashForm(forms.ModelForm):
    class Meta:
        model = Cash
        fields = ['name', 'comment', 'is_prepayment',
                  'currency', 'fee_absolute_value', 'fee_relative_value', 'fee_tax_rate', ]

    def save(self, request=None, commit=True):
        new_cash = super(CashForm, self).save(commit=False)
        new_cash.owner = request.actor
        if commit:
            new_cash.save()
        return new_cash
