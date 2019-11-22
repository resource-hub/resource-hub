from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.forms.models import model_to_dict
from smtplib import SMTPException

from core.forms import *
from core.models import *
from core.tables import OrganizationsTable, MembersTable
from core.tokens import TokenGenerator
from core.decorators import organization_admin_required


def index(request):
    return render(request, 'core/index.html')


def support(request):
    issue_form = ReportIssueForm()
    if request.method == 'POST':
        issue_form = ReportIssueForm(request.POST)

        if issue_form.is_valid():
            try:
                issue_form.post()
                message = _('Your issue has been posted!')
                messages.add_message(request, messages.SUCCESS, message)
            except IOError:
                message = _('Your issue could not be posted!')
                messages.add_message(request, messages.ERROR, message)

            return redirect(reverse('core:support'))

    context = {
        'issue_form': issue_form,
    }

    return render(request, 'core/support.html', context)


def language(request):
    return render(request, 'core/language.html')


def register(request):
    if request.method == 'POST':
        user_form = UserBaseForm(request.POST)
        info_form = InfoForm(request.POST, request.FILES)
        address_form = AddressForm(request.POST)
        bank_account_form = BankAccountForm(request.POST)

        if (user_form.is_valid() and
                info_form.is_valid() and
                address_form.is_valid() and
                bank_account_form.is_valid()):

            new_bank_account = bank_account_form.save()
            new_address = address_form.save()

            new_info = info_form.save(commit=False)
            new_info.address = new_address
            new_info.bank_account = new_bank_account
            new_info.save()

            new_user = user_form.save(commit=False)
            new_user.info = new_info
            new_user.is_active = False
            new_user.save()
            Actor.objects.create(user=new_user)

            current_site = get_current_site(request)
            subject = _('Activate your account')
            token_generator = TokenGenerator()

            message = render_to_string('core/activation_mail.html', {
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': token_generator.make_token(new_user),
            })

            recipient = user_form.cleaned_data.get('email')
            email = EmailMultiAlternatives(
                subject,
                message,
                to=[recipient],
            )
            email.attach_alternative(message, 'text/html')

            try:
                email.send(fail_silently=False)
            except SMTPException as e:
                message = _('The activation-email could not be sent')
                messages.add_message(request, messages.ERROR, message)
                return redirect(reverse('core:login'))

            message = _(
                'Please confirm your email address to complete the registration')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('core:login'))
    else:
        if request.user.is_authenticated:
            message = _('You are already logged in.')
            messages.add_message(request, messages.INFO, message)
            return redirect(reverse('core:admin'))
        else:
            user_form = UserBaseForm()
            info_form = InfoForm()
            address_form = AddressForm()
            bank_account_form = BankAccountForm()

    context = {
        'user_form': user_form,
        'info_form': info_form,
        'address_form': address_form,
        'bank_account_form': bank_account_form,
    }

    return render(request, 'core/register.html', context)


def activate(request, uidb64, token):
    token_generator = TokenGenerator()
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        message = _('Your account has been activated successfully.')
        messages.add_message(request, messages.SUCCESS, message)
        return redirect(reverse('core:admin'))
    else:
        message = _('Your activation-link is invalid!')
        messages.add_message(request, messages.ERROR, message)
        return redirect(reverse('core:login'))


def custom_login(request):
    if request.user.is_authenticated:
        # set inital role always as user
        request.session['role'] = User.Role.USER
        return redirect(reverse('core:admin'))
    else:
        return LoginView.as_view(
            template_name='core/login.html')(request)


@login_required
def set_role(request):
    if request.method == "POST":

        return
    return


# Internal admin section

@login_required
def admin(request):
    return render(request, 'core/admin/index.html')


@login_required
def account_profile(request, scope):
    user = request.user
    info = model_to_dict(user.info)
    address = model_to_dict(user.info.address)
    bank_account = model_to_dict(user.info.bank_account)

    info_form = InfoForm(initial=info)
    address_form = AddressForm(initial=address)
    bank_account_form = BankAccountForm(initial=bank_account)

    if request.method == 'POST':
        if scope == 'info':
            info_form = InfoForm(
                request.POST, request.FILES, instance=user.info)

            if info_form.is_valid():
                info_form.save()
                message = _('Your information has been updated')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('core:account_profile', kwargs={'scope': 'info'}))

        elif scope == 'address':
            address_form = AddressForm(
                request.POST, instance=user.info.address)

            if address_form.is_valid():
                address_form.save()
                message = _('Your address has been updated')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('core:account_profile', kwargs={'scope': 'address'}))

        elif scope == 'bank_account':
            bank_account_form = BankAccountForm(
                request.POST, instance=user.info.bank_account)

            if bank_account_form.is_valid():
                bank_account_form.save()
                message = _('Your bank information has been updated')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('core:account_profile', kwargs={'scope': 'bank_account'}))

    context = {
        'info_form': info_form,
        'address_form': address_form,
        'bank_account_form': bank_account_form,
        scope: 'active',
    }
    return render(request, 'core/admin/account_profile.html', context)


@login_required
def account_settings(request, scope):
    user = request.user
    email_form = EmailChangeForm(user, initial={
        'old_email': user.email,
    })
    password_form = PasswordChangeForm(user)

    if request.method == 'POST':
        if scope == 'email':
            email_form = EmailChangeForm(user, request.POST)

            if email_form.is_valid():
                email_form.save()
                message = _('Your email has been updated successfully.')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('core:account_settings', kwargs={'scope': 'email'}))

        elif scope == 'password':
            password_form = PasswordChangeForm(user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)

                message = _('Your password has been updated successfully.')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('core:account_settings', kwargs={'scope': 'password'}))

    context = {
        'email_form': email_form,
        'password_form': password_form,
        scope: 'active',
    }
    return render(request, 'core/admin/account_settings.html', context)


@login_required
def organizations(request):
    user = request.user
    organizations = Organization.objects.all().filter(members__pk=user.id)

    if organizations:
        data = []
        for o in organizations:
            role = OrganizationMember.get_role(user, o)
            data.append({
                'name': o.name,
                'role': role,
                'id': o.id,
            })
        organizations_table = OrganizationsTable(data)
    else:
        organizations_table = None

    context = {
        'organizations_table': organizations_table,
    }
    return render(request, 'core/admin/organizations.html', context)


@login_required
def organizations_register(request):
    user = request.user
    organization_form = OrganizationForm()
    info_form = InfoForm()
    address_form = AddressForm()
    bank_account_form = BankAccountForm()

    if request.method == 'POST':
        organization_form = OrganizationForm(request.POST)
        info_form = InfoForm(request.POST, request.FILES)
        address_form = AddressForm(request.POST)
        bank_account_form = BankAccountForm(request.POST)

        if (organization_form.is_valid() and
                info_form.is_valid() and
                address_form.is_valid() and
                bank_account_form.is_valid()):

            new_organization = organization_form.save(commit=False)
            new_address = address_form.save()
            new_bank_account = bank_account_form.save()

            new_info = info_form.save(commit=False)
            new_info.address = new_address
            new_info.bank_account = new_bank_account
            new_info.save()

            new_organization.info = new_info
            new_organization.save()
            new_organization.members.add(user, through_defaults={
                                         'role': OrganizationMember.ADMIN})
            Actor.objects.create(user=user, organization=new_organization)

            message = _('The organization has been registered')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('core:organizations'))

    context = {
        'organization_form': organization_form,
        'info_form': info_form,
        'address_form': address_form,
        'bank_account_form': bank_account_form,
    }
    return render(request, 'core/admin/organizations_register.html', context)


@login_required
def organizations_profile(request, id):
    user = request.user
    organization = get_object_or_404(Organization, pk=id)

    context = {
        'organization': organization,
        'is_admin': OrganizationMember.is_admin(user, organization),
    }

    return render(request, 'core/admin/organizations_profile.html', context)


@login_required
@organization_admin_required
def organizations_profile_edit(request, id, scope):
    organization = get_object_or_404(Organization, pk=id)

    info = model_to_dict(organization.info)
    address = model_to_dict(organization.info.address)
    bank_account = model_to_dict(organization.info.bank_account)

    info_form = InfoForm(initial=info)
    address_form = AddressForm(initial=address)
    bank_account_form = BankAccountForm(initial=bank_account)

    if request.method == 'POST':
        if scope == 'info':
            info_form = InfoForm(
                request.POST, request.FILES, instance=organization.info)

            if info_form.is_valid():
                info_form.save()
                message = _('Your information has been updated')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('core:organizations_profile_edit', kwargs={'scope': 'info',
                                                                                   'id': id, }))

        elif scope == 'address':
            address_form = AddressForm(
                request.POST, instance=organization.info.address)

            if address_form.is_valid():
                address_form.save()
                message = _('Your address has been updated')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('core:organizations_profile_edit', kwargs={'scope': 'address',
                                                                                   'id': id, }))

        elif scope == 'bank_account':
            bank_account_form = BankAccountForm(
                request.POST, instance=organization.info.bank_account)

            if bank_account_form.is_valid():
                bank_account_form.save()
                message = _('Your bank information has been updated')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('core:organizations_profile_edit',
                                        kwargs={
                                            'id': id, }))

    context = {
        'organization_name': organization.name,
        'info_form': info_form,
        'address_form': address_form,
        'bank_account_form': bank_account_form,
        scope: 'active',
    }
    return render(request, 'core/admin/organizations_profile_edit.html', context)


@login_required
@organization_admin_required
def organizations_members(request, id):
    user = request.user
    organization = get_object_or_404(Organization, pk=id)
    members = organization.members.select_related().all()

    if members:
        data = []
        for m in members:
            role = OrganizationMember.get_role(m, organization)
            data.append({
                'id': m.id,
                'username': m.username,
                'first_name': m.first_name,
                'last_name': m.last_name,
                'role': role,
            })
        members_table = MembersTable(data)
    else:
        members_table = None

    context = {
        'members_table': members_table,
        'organization': organization,
    }
    return render(request, 'core/admin/organizations_members.html', context)


@login_required
@organization_admin_required
def organizations_members_add(request, id):
    organization = get_object_or_404(Organization, pk=id)
    member_add_form = OrganizationMemberAddForm(organization=organization)

    if request.method == 'POST':
        member_add_form = OrganizationMemberAddForm(organization,
                                                    request.POST)

        if member_add_form.is_valid():
            member_add_form.save()

            message = _('User has been added to ' + organization.name)
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('core:organizations_members', kwargs={'id': id}))

    context = {
        'member_add_form': member_add_form,
        'organization': organization,
    }
    return render(request, 'core/admin/organizations_members_add.html', context)
