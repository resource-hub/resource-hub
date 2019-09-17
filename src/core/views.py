from django.contrib import messages
from django.contrib.auth import login, authenticate, update_session_auth_hash
from django.contrib.auth.views import LoginView
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
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
from core.tokens import TokenGenerator


def index(request):
    return render(request, 'core/index.html')


def register(request):
    if request.method == 'POST':
        user_form = UserBaseForm(request.POST)
        info_form = InfoForm(request.POST)
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
            return redirect(reverse('core:account'))
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


def activate_account(request):
    return render(request, 'core/activate_account.html')


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
        return redirect(reverse('core:account'))
    else:
        message = _('Your activation-link is invalid!')
        messages.add_message(request, messages.ERROR, message)
        return redirect(reverse('core:login'))


def custom_login(request):
    if request.user.is_authenticated:
        return redirect(reverse('core:account'))
    else:
        return LoginView.as_view(
            template_name='core/login.html')(request)


# Internal account section

@login_required
def account(request):
    return render(request, 'core/account/index.html')


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
                return redirect(reverse('core:account-settings', kwargs={'scope': 'email'}))

        elif scope == 'password':
            password_form = PasswordChangeForm(user, request.POST)

            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)

                message = _('Your password has been updated successfully.')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('core:account-settings', kwargs={'scope': 'password'}))

    context = {
        'email_form': email_form,
        'password_form': password_form,
        scope: 'active',
    }
    return render(request, 'core/account/settings.html', context)


@login_required
def account_information(request, scope):
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
                return redirect(reverse('core:account-information', kwargs={'scope': 'info'}))

        elif scope == 'address':
            address_form = AddressForm(
                request.POST, instance=user.info.address)

            if address_form.is_valid():
                address_form.save()
                message = _('Your address has been updated')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('core:account-information', kwargs={'scope': 'address'}))

        elif scope == 'bank_account':
            bank_account_form = BankAccountForm(
                request.POST, instance=user.info.bank_account)

            if bank_account_form.is_valid():
                bank_account_form.save()
                message = _('Your bank information has been updated')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('core:account-information', kwargs={'scope': 'bank_account'}))

    context = {
        'info_form': info_form,
        'address_form': address_form,
        'bank_account_form': bank_account_form,
        scope: 'active',
    }
    return render(request, 'core/account/information.html', context)
