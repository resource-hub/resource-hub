from datetime import datetime
from schwifty import IBAN, BIC
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.utils.dateparse import parse_date
from core.models import *


class UserBaseForm(UserCreationForm):
    birth_date = forms.CharField(
        widget=forms.widgets.DateTimeInput(attrs={"type": "date"}))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'birth_date', 'password1', 'password2', )

    def clean(self):
        super().clean()

    def clean_birth_date(self):
        OLDEST_PERSON = 44694
        MINIMUM_AGE = 2555
        birth_date = parse_date(
            self.cleaned_data['birth_date'])
        now = datetime.now().date()
        age = abs((now - birth_date).days)

        if age > OLDEST_PERSON:
            raise forms.ValidationError(
                _('Are you older than the oldest person ever alive?'),
                code='too-old')

        if age < MINIMUM_AGE:
            raise forms.ValidationError(
                _('You have to be older than 16 to sign up'), code='too-young')
        return self.cleaned_data['birth_date']


class InfoForm(forms.ModelForm):
    class Meta:
        model = Info
        exclude = ['address', 'bank_account',
                   'created_by', 'updated_by', ]


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        exclude = ['address', 'bank_account',
                   'created_by', 'updated_by', ]


class BankAccountForm(forms.ModelForm):
    class Meta:
        model = BankAccount
        exclude = ['address', 'bank_account',
                   'created_by', 'updated_by', ]

    def clean_iban(self):
        iban = self.cleaned_data['iban']
        if iban:
            try:
                IBAN(iban)
            except ValueError as e:
                raise forms.ValidationError(
                    _('Invalid IBAN: ') + str(e), code='invalid-iban')
        return iban

    def clean_bic(self):
        bic = self.cleaned_data['bic']
        if bic:
            try:
                BIC(bic)
            except ValueError as e:
                raise forms.ValidationError(
                    _('Invalid BIC: ') + str(e), code='invalid-bic')
        return bic


class EditBaseUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
