from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from core.models import *


class UserBaseForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'birth_date', 'password1', 'password2', )

    def clean(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Email exists")
        return self.cleaned_data


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
