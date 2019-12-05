from datetime import datetime
import requests
from schwifty import IBAN, BIC

from django import forms
from django.conf import settings
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.forms import model_to_dict
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


class InfoFormManager():
    def __init__(self, request=None):
        if request is None:
            self.info_form = InfoForm()
            self.address_form = AddressForm()
            self.bank_account_form = BankAccountForm()
        else:
            self.info_form = InfoForm(request.POST, request.FILES)
            self.address_form = AddressForm(request.POST)
            self.bank_account_form = BankAccountForm(request.POST)

    def get_forms(self):
        return {
            'info_form': self.info_form,
            'address_form': self.address_form,
            'bank_account_form': self.bank_account_form,
        }

    def is_valid(self):
        return (self.info_form.is_valid() and
                self.address_form.is_valid() and
                self.bank_account_form.is_valid())

    def save(self):
        new_bank_account = self.bank_account_form.save()
        new_address = self.address_form.save()

        new_info = self.info_form.save(commit=False)
        new_info.address = new_address
        new_info.bank_account = new_bank_account
        new_info.save()

        return new_info


class UserFormManager():
    def __init__(self, request=None):
        if request is None:
            self.user_form = UserBaseForm()
            self.info_form = InfoFormManager()
        else:
            self.user_form = UserBaseForm(request.POST)
            self.info_form = InfoFormManager(request)

    def get_forms(self):
        forms = self.info_form.get_forms()
        forms['user_form'] = self.user_form
        return forms

    def is_valid(self):
        return (self.user_form.is_valid() and
                self.info_form.is_valid())

    def save(self):
        new_info = self.info_form.save()

        new_user = self.user_form.save(commit=False)
        new_user.info = new_info
        new_user.save()
        Actor.objects.create(user=new_user)
        return new_user


class ProfileFormManager():
    def __init__(self, request, entity):
        self.is_valid = True
        self.request = request
        self.entity = entity
        self.info_form = InfoForm(initial=model_to_dict(self.entity.info))
        self.address_form = AddressForm(
            initial=model_to_dict(self.entity.info.address))
        self.bank_account_form = BankAccountForm(
            initial=model_to_dict(self.entity.info.bank_account))

    def change_info(self):
        self.info_form = InfoForm(
            self.request.POST, self.request.FILES, instance=self.entity.info)

        if self.info_form.is_valid():
            self.info_form.save()
        else:
            self.is_valid = False

    def change_address(self):
        self.address_form = AddressForm(
            self.request.POST, instance=self.entity.info.address)

        if self.address_form.is_valid():
            self.address_form.save()
        else:
            self.is_valid = False

    def change_bank_account(self):
        self.bank_account_form = BankAccountForm(
            self.request.POST, instance=self.entity.info.bank_account)

        if self.bank_account_form.is_valid():
            self.bank_account_form.save()
        else:
            self.is_valid = False

    def get_forms(self, scope):
        return {
            'info_form': self.info_form,
            'address_form': self.address_form,
            'bank_account_form': self.bank_account_form,
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
        user = User.objects.filter(pk=self.user.id).update(email=new_email)


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


class OrganizationFormManager():
    def __init__(self, request=None):
        if request is None:
            self.organization_form = OrganizationForm()
            self.info_form = InfoFormManager()
        else:
            self.request = request
            self.organization_form = OrganizationForm(request.POST)
            self.info_form = InfoFormManager(request)

    def get_forms(self):
        forms = self.info_form.get_forms()
        forms['organization_form'] = self.organization_form
        return forms

    def is_valid(self):
        return (self.organization_form.is_valid() and
                self.info_form.is_valid())

    def save(self):
        user = self.request.user
        new_info = self.info_form.save()

        new_organization = self.organization_form.save(commit=False)
        new_organization.info = new_info
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
            raise ValidationError("Invalid Membership form")

        return new_organization


class OrganizationMemberAddForm(forms.Form):
    def __init__(self, organization,  *args, **kwargs):
        self.organization = organization
        super(OrganizationMemberAddForm, self).__init__(*args, **kwargs)

    username = forms.CharField(
        max_length=128,
        required=True,

        widget=forms.TextInput(
            attrs={'class': 'prompt', 'id': 'search', 'autofocus': 'autofocus'}),
    )
    role = forms.ChoiceField(choices=OrganizationMember.ORGANIZATION_ROLES)

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username=username)
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

    def clean_role(self):
        # todo: clean role
        role = self.cleaned_data['role']
        return role

    def save(self):
        username = self.cleaned_data['username']
        role = self.cleaned_data['role']

        user = User.objects.get(username=username)
        self.organization.members.add(user, through_defaults={'role': role})
        member = OrganizationMember.objects.get(
            organization=self.organization, user=user)
        # create actor object if user is allowed to act for organization
        if member.is_admin():
            Actor.objects.create(user=user, organization=self.organization)


class RoleChangeForm(forms.Form):
    actor_id = forms.IntegerField()

    def __init__(self, user, *args, **kwargs):
        super(RoleChangeForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_actor_id(self):
        actor_id = self.cleaned_data['actor_id']
        try:
            actor = Actor.objects.get(pk=actor_id)
        except Actor.DoesNotExist:
            raise forms.ValidationError(
                _('Actor does not exist'), code='actor-not-exists')

        if actor.user.id != self.user.id:
            raise forms.ValidationError(
                _('Actor not associated with user'), code='actor-user-not-associated')
        return actor_id

    def save(self, request):
        actor_id = self.cleaned_data['actor_id']
        request.session['actor_id'] = actor_id
        return request


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        exclude = ['address','updated_at', 'updated_by']



class ReportIssueForm(forms.Form):
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
        API_TOKEN = settings.API_TOKEN
        payload = {"title": title, "description": description}
        headers = {"PRIVATE-TOKEN": API_TOKEN, "Accept-Charset": "UTF-8"}
        r = requests.post(URL, data=payload, headers=headers)

        if r.status_code != 201:
            raise IOError(
                'Issue not successfully created. POST request exited with: ' + r.status_code)
