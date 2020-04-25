import re
from datetime import datetime

import bleach
import requests
from django import forms
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm, UserCreationForm
from django.contrib.auth.hashers import check_password
from django.forms import inlineformset_factory
from django.utils.dateparse import parse_date
from django.utils.translation import ugettext_lazy as _

from schwifty import BIC, IBAN

from .fields import HTMLField
from .models import (Actor, Address, BankAccount, ContractProcedure,
                     ContractTrigger, Location, Organization,
                     OrganizationMember, PaymentMethod, Price, PriceProfile,
                     User)
from .utils import get_associated_objects
from .widgets import IBANInput, UISearchField


class FormManager():
    forms = {}

    def __init__(self, request=None, instances=None):
        self.request = request
        for k, form in self.forms.items():
            instance = instances[k] if instances else None

            # check if reference has bin initiazlied already
            if not callable(form):
                form = form.__class__

            self.forms[k] = form(
                data=request.POST,
                files=request.FILES, instance=instance
            ) if request else form(instance=instance)

    def get_forms(self):
        return self.forms

    def is_valid(self):
        is_valid = True
        for form in self.forms.values():
            if not form.is_valid():
                is_valid = False
        return is_valid

    def save(self, commit=True):
        raise NotImplementedError()


class ActorForm(forms.ModelForm):
    info_text = HTMLField(required=False)

    class Meta:
        model = Actor
        fields = ['image', 'telephone_public', 'telephone_private',
                  'email_public', 'website', 'info_text']


class UserBaseForm(UserCreationForm):
    first_name = forms.CharField(label=_('First name'), required=True)
    last_name = forms.CharField(label=_('Last name'), required=True)
    birth_date = forms.CharField(
        widget=forms.widgets.DateTimeInput(attrs={"type": "date"}))
    info_text = HTMLField(required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name',
                  'email', 'birth_date', 'password1', 'password2', 'image', 'telephone_public', 'telephone_private',
                  'email_public', 'website', 'info_text']

    def clean_info_text(self):
        return bleach.clean(self.cleaned_data['info_text'])

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
    email_public = forms.EmailField(required=True, help_text=_(
        'This is the mail will be displayed on bills and on the profile'))
    info_text = HTMLField(required=False)

    def clean_name(self):
        name = self.cleaned_data['name']
        try:
            Organization.objects.get(name__iexact=name.lower())
        except Organization.DoesNotExist:
            return name

        raise forms.ValidationError(
            _('This organization name already exists'), code='organization-name-exists')

    def clean_email_public(self):
        if not self.cleaned_data['email_public']:
            raise forms.ValidationError(
                _('For organizations, a public email is required'))
        return self.cleaned_data['email_public']

    class Meta:
        model = Organization
        fields = ['name', 'email_public', 'image', 'telephone_public', 'telephone_private',
                  'website', 'info_text']


class InvoicingSettings(forms.ModelForm):
    class Meta:
        model = Actor
        fields = ['tax_id', 'vat_id', 'invoice_logo_image', 'invoice_numbers_prefix', 'invoice_numbers_prefix_cancellations',
                  'invoice_introductory_text', 'invoice_additional_text', 'invoice_footer_text']


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['street', 'street_number',
                  'postal_code', 'city', 'country', ]

    def clean_postal_code(self):
        postal_code = self.cleaned_data['postal_code']
        if not postal_code:
            return
        if re.fullmatch(r'^[0-9]{5}$', postal_code):
            return postal_code
        raise forms.ValidationError(
            _('Invalid postal code'), code='invalid-postal-code')


class BankAccountForm(forms.ModelForm):
    account_holder = forms.CharField(max_length=70, label=_('Account holder'))
    iban = forms.CharField(widget=IBANInput(), label=_('IBAN'))
    bic = forms.CharField(max_length=11, label=_('BIC'))

    class Meta:
        model = BankAccount
        fields = ['account_holder', 'iban', 'bic', ]

    def clean_iban(self):
        iban = self.cleaned_data['iban'].replace(' ', '').upper()
        if iban:
            try:
                IBAN(iban)
            except ValueError as e:
                raise forms.ValidationError(
                    _('Invalid IBAN: ') + str(e), code='invalid-iban')
        return iban

    def clean_bic(self):
        bic = self.cleaned_data['bic'].upper()
        if bic:
            try:
                BIC(bic)
            except ValueError as e:
                raise forms.ValidationError(
                    _('Invalid BIC: ') + str(e), code='invalid-bic')
        return bic


class UserFormManager():
    def __init__(self, request=None):
        if request is None:
            self.user_form = UserBaseForm()
            self.address_form = AddressForm()
            self.bank_account_form = BankAccountForm()
        else:
            self.user_form = UserBaseForm(request.POST, request.FILES)
            self.address_form = AddressForm(request.POST)
            self.bank_account_form = BankAccountForm(request.POST)

    def get_forms(self):
        return {
            'user_form': self.user_form,
            'address_form': self.address_form,
            'bank_account_form': self.bank_account_form,
        }

    def is_valid(self):
        return (self.user_form.is_valid() and
                self.address_form.is_valid() and
                self.bank_account_form.is_valid())

    def save(self):
        new_bank_account = self.bank_account_form.save()
        new_address = self.address_form.save()

        new_user = self.user_form.save(commit=False)
        new_user.name = new_user.first_name + ' ' + new_user.last_name
        new_user.address = new_address
        new_user.bank_account = new_bank_account
        new_user.save()

        return new_user


class ProfileFormManager():
    def __init__(self, request, actor):
        self.is_valid = True
        self.request = request
        self.actor = actor
        self.actor_form = ActorForm(instance=self.actor)
        self.address_form = AddressForm(
            instance=self.actor.address)
        self.bank_account_form = BankAccountForm(
            instance=self.actor.bank_account)
        self.invoicing_settings_form = InvoicingSettings(
            instance=self.actor
        )

    def change_info(self):
        self.actor_form = ActorForm(
            self.request.POST, self.request.FILES, instance=self.actor)

        if self.actor_form.is_valid():
            self.actor_form.save()
        else:
            self.is_valid = False

    def change_address(self):
        self.address_form = AddressForm(
            self.request.POST, instance=self.actor.address)

        if self.address_form.is_valid():
            self.address_form.save()
        else:
            self.is_valid = False

    def change_bank_account(self):
        self.bank_account_form = BankAccountForm(
            self.request.POST, instance=self.actor.bank_account)

        if self.bank_account_form.is_valid():
            self.bank_account_form.save()
        else:
            self.is_valid = False

    def change_invoicing_settings(self):
        self.invoicing_settings_form = InvoicingSettings(
            self.request.POST, self.request.FILES, instance=self.actor,
        )
        if self.invoicing_settings_form.is_valid():
            self.invoicing_settings_form.save()
        else:
            self.is_valid = False

    def get_forms(self, scope):
        return {
            'actor_form': self.actor_form,
            'address_form': self.address_form,
            'bank_account_form': self.bank_account_form,
            'invoicing_settings_form': self.invoicing_settings_form,
            scope: 'active',
        }


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
        User.objects.get(pk=self.user.id).update(email=new_email)


class UserAccountFormManager():
    def __init__(self, request):
        self.request = request
        self.user = request.user
        self.email_form = EmailChangeForm(self.user, initial={
            'old_email': self.user.email,
        })
        self.password_form = PasswordChangeForm(self.user)
        self.is_valid = True

    def change_email(self):
        self.email_form = EmailChangeForm(self.user, self.request.POST)

        if self.email_form.is_valid():
            self.email_form.save()
        else:
            self.is_valid = False

    def change_password(self):
        self.password_form = PasswordChangeForm(self.user, self.request.POST)

        if self.password_form.is_valid():
            update_session_auth_hash(self.request, self.user)
            self.password_form.save()
        else:
            self.is_valid = False

    def get_forms(self, scope):
        return {
            'email_form': self.email_form,
            'password_form': self.password_form,
            scope: 'active',
        }


class ContractProcedureForm(forms.ModelForm):
    def __init__(self, request, *args, **kwargs):
        self.request = request
        super(ContractProcedureForm, self).__init__(*args, **kwargs)
        self.fields['payment_methods'].queryset = get_associated_objects(
            request.actor,
            PaymentMethod
        ).select_subclasses()
        self.fields['triggers'].queryset = get_associated_objects(
            request.actor,
            ContractTrigger
        )

    terms_and_conditions = HTMLField()

    class Meta:
        model = ContractProcedure
        fields = ['name', 'auto_accept', 'is_invoicing', 'terms_and_conditions', 'notes',
                  'triggers', 'tax_rate', 'payment_methods', 'settlement_interval', ]


class PriceForm(forms.ModelForm):

    class Meta:
        model = Price
        fields = ['addressee', 'value', 'currency', 'discounts', ]
        help_text = {
            'discounts': _('Apply discounts from prices profiles?'),
        }


class PriceProfileForm(forms.ModelForm):
    class Meta:
        model = PriceProfile
        fields = ['addressee', 'description', 'discount', ]
        help_texts = {
            'addressee': _('When left empty, the discount is visible for everyone')
        }


PriceProfileFormSet = inlineformset_factory(
    ContractProcedure, PriceProfile, form=PriceProfileForm, extra=1)


class OrganizationFormManager():
    def __init__(self, request=None):
        if request is None:
            self.organization_form = OrganizationForm()
            self.address_form = AddressForm()
            self.bank_account_form = BankAccountForm()
        else:
            self.request = request
            self.organization_form = OrganizationForm(
                request.POST, request.FILES)
            self.address_form = AddressForm(request.POST)
            self.bank_account_form = BankAccountForm(request.POST)

    def get_forms(self):
        return {
            'organization_form': self.organization_form,
            'address_form': self.address_form,
            'bank_account_form': self.bank_account_form,
        }

    def is_valid(self):
        return (self.organization_form.is_valid() and
                self.address_form.is_valid() and
                self.bank_account_form.is_valid())

    def save(self):
        user = self.request.user
        new_bank_account = self.bank_account_form.save()
        new_address = self.address_form.save()

        new_organization = self.organization_form.save(commit=False)
        new_organization.name = self.organization_form.cleaned_data['name']
        new_organization.bank_account = new_bank_account
        new_organization.address = new_address
        new_organization.save()

        membership = OrganizationMemberAddForm(
            new_organization,
            {
                'username': user.username,
                'role': OrganizationMember.OWNER
            }
        )
        if membership.is_valid():
            membership.save()
        else:
            raise forms.ValidationError("Invalid Membership form")

        return new_organization


class OrganizationMemberAddForm(forms.Form):
    def __init__(self, organization, *args, **kwargs):
        self.organization = organization
        super(OrganizationMemberAddForm, self).__init__(*args, **kwargs)

    username = forms.CharField(
        max_length=128,
        required=True,
        widget=UISearchField(attrs={'autofocus': 'autofocus'}),
    )
    role = forms.ChoiceField(choices=OrganizationMember.ORGANIZATION_ROLES)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            raise forms.ValidationError(
                _('The user does not exist.'), code='user-not-exists')

        try:
            Organization.objects.get(
                pk=self.organization.id, members__username=username)
            raise forms.ValidationError(
                _('User is already a member'), code='user-already-member')
        except Organization.DoesNotExist:
            return username

    def save(self):
        username = self.cleaned_data['username']
        role = self.cleaned_data['role']

        user = User.objects.get(username=username)
        self.organization.members.add(user, through_defaults={'role': role})


class RoleChangeForm(forms.Form):
    actor_id = forms.IntegerField()

    def __init__(self, user, *args, **kwargs):
        super(RoleChangeForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_actor_id(self):
        actor_id = self.cleaned_data['actor_id']

        try:
            Actor.objects.get(pk=actor_id)
        except Actor.DoesNotExist:
            raise forms.ValidationError(
                _('Actor does not exist'), code='actor-not-exists')

        if actor_id != self.user.id:
            try:
                OrganizationMember.objects.get(organization=actor_id,
                                               user=self.user, role__gte=OrganizationMember.ADMIN)
            except OrganizationMember.DoesNotExist:
                raise forms.ValidationError(
                    _('Actor not associated with user'), code='actor-user-not-associated')
        return actor_id

    def save(self, request):
        actor_id = self.cleaned_data['actor_id']
        request.session['actor_id'] = actor_id
        return request


class LocationForm(forms.ModelForm):
    search = forms.CharField(widget=UISearchField, required=False, help_text=_(
        'You can use this search field for the address to autofill the location data!'))
    description = HTMLField()

    class Meta:
        model = Location
        fields = ['name', 'is_public', 'description', 'image',
                  'search', 'latitude', 'longitude']
        help_texts = {
            'is_public': _('Allow other users to link information to this location'),
        }

    def save(self, owner=None, commit=True):
        new_location = super(LocationForm, self).save(commit=False)
        if owner is not None:
            new_location.owner = owner
        if commit:
            new_location.save()
        return new_location


class LocationFormManager(FormManager):
    forms = {
        'location_form': LocationForm,
        'address_form': AddressForm,
    }

    def save(self, commit=True):
        owner = self.request.actor
        user = self.request.user
        new_address = self.forms['address_form'].save()
        new_location = self.forms['location_form'].save(owner, commit=False)
        new_location.created_by = user
        new_location.address = new_address
        if commit:
            new_location.save()
        return new_location


class ReportBugForm(forms.Form):
    title = forms.CharField(
        max_length=128,
        help_text=_(
            'In what part of the software is the issue or your request?'),
    )
    description = forms.CharField(
        widget=forms.Textarea,
        help_text=_(
            'Short description of the problem or the feature you want to see implemented'),
    )

    def post(self):
        title = self.cleaned_data['title']
        description = self.cleaned_data['description']

        URL = "https://gitlab.com/api/v4/projects/13767519/issues"
        GITLAB_TOKEN = settings.GITLAB_TOKEN
        payload = {"title": title, "description": description}
        headers = {"PRIVATE-TOKEN": GITLAB_TOKEN, "Accept-Charset": "UTF-8"}
        r = requests.post(URL, data=payload, headers=headers)

        if r.status_code != 201:
            import json
            content = json.loads(r.content)
            raise IOError(
                'Issue not successfully created. POST request exited with: ' + str(r.status_code) + ' Msg:' + content['message']['error'])
