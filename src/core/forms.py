from datetime import datetime
from schwifty import IBAN, BIC
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import check_password
from django.utils.translation import ugettext_lazy as _
from django.utils.dateparse import parse_date
from core.models import *


class UserBaseForm(UserCreationForm):
    birth_date = forms.CharField(
        widget=forms.widgets.DateTimeInput(attrs={"type": "date"}))
    name_public = forms.BooleanField(help_text=_(
        'Display your name to other users so they can find you'), initial=True)

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


class OrganizationForm(forms.ModelForm):
    name = forms.CharField(max_length=100, label=_(
        'Organization name'), help_text=_('Please include your legal form'))

    class Meta:
        model = Organization
        fields = ['name', ]


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


class EmailChangeForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        if user is None:
            raise ValueError('User object is none')
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    old_email = forms.EmailField()
    new_email1 = forms.EmailField(
        label=_('New email-address')
    )
    new_email2 = forms.EmailField(
        label=_('New email-address confirmation')
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput()
    )

    def clean_new_email2(self):
        old_email = self.cleaned_data['old_email']
        new_email1 = self.cleaned_data['new_email1']
        new_email2 = self.cleaned_data['new_email2']

        if new_email1 != new_email2:
            raise forms.ValidationError(
                _('The email-addresses do not match'),
                code='not-matching-email'
            )

        if old_email == new_email2:
            raise forms.ValidationError(
                _('The new email is identical to the old one'),
                code='identical-mail'
            )

        return new_email1

    def clean_password(self):
        sent_password = self.cleaned_data['password']
        curr_password = User.objects.get(pk=self.user.id).password

        if check_password(sent_password, curr_password):
            return sent_password
        else:
            raise forms.ValidationError(
                _('The password is incorrect'), code='incorrect-password')

    def save(self):
        new_email = self.cleaned_data['new_email1']
        user = User.objects.filter(pk=self.user.id).update(email=new_email)


class OrganizationMemberAddForm(forms.Form):
    def __init__(self, organization_id,  *args, **kwargs):
        self.organization_id = organization_id
        super(OrganizationMemberAddForm, self).__init__(*args, **kwargs)

    username = forms.CharField(
        max_length=128,
        required=True,

        widget=forms.TextInput(
            attrs={'class': 'prompt', 'id': 'search', 'autofocus': 'autofocus'}),
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(
                _('The user does not exist.'), code='user-not-exists')

        try:
            Organization.objects.get(
                pk=self.organization_id, members__username=username)
            raise forms.ValidationError(
                _('User is already a member'), code='user-already-member')
        except Organization.DoesNotExist:
            return username
