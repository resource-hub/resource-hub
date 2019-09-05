from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import render, redirect
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
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

            message = render_to_string('core/account/activation_mail.html', {
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
                messages.add_message(request, messages.ERROR, str(e))
                return redirect(reverse('core:login'))

            message = _(
                'Please confirm your email address to complete the registration')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('core:login'))
    else:
        if request.user.is_authenticated:
            message = _('You are already logged in.')
            messages.add_message(request, messages.INFO, message)
            return redirect(reverse('core:profile'))
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

    return render(request, 'core/account/register.html', context)


def activate_account(request):
    return render(request, 'core/account/activate_account.html')


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
        return redirect(reverse('core:profile'))
    else:
        message = _('Your activation-link is invalid!')
        messages.add_message(request, messages.ERROR, message)
        return redirect(reverse('core:login'))


def custom_login(request):
    if request.user.is_authenticated:
        return redirect(reverse('core:profile'))
    else:
        return LoginView.as_view(
            template_name='core/account/login.html')(request)


def profile(request):
    if request.user.is_authenticated:
        user_id = request.user.id
        user_info = User.objects.select_related().get(id=user_id)
        form = UserBaseForm({'first_name': 'test'})

        context = {'form': form}
        return render(request, 'core/account/profile.html', context)
    else:
        return redirect(reverse('core:login'))
