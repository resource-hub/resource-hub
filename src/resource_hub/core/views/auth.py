
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views import View

from resource_hub.core.forms import RoleChangeForm, UserFormManager
from resource_hub.core.jobs import send_mail
from resource_hub.core.models import Notification, User
from resource_hub.core.tokens import TokenGenerator
from resource_hub.core.utils import language


def send_verification_mail(user, request):
    subject = _('Activate your account')
    token_generator = TokenGenerator()
    link = request.build_absolute_uri(reverse('core:verify', kwargs={
        'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
        'token':  token_generator.make_token(user),
    }))

    message = render_to_string('core/mail_verification.html', context={
        'user': user,
        'link': link,
    })
    recipient = user.email
    send_mail.delay(subject, message, [recipient])


class Register(View):
    template_name = 'core/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            message = _('You are already logged in.')
            messages.add_message(request, messages.INFO, message)
            return redirect(reverse('control:home'))

        user_form = UserFormManager(request.user, request.actor)
        return render(request, 'core/register.html', user_form.get_forms())

    def post(self, request):
        user_form = UserFormManager(
            request.user, request.actor, data=request.POST, files=request.FILES)

        if (user_form.is_valid()):
            with transaction.atomic():
                new_user = user_form.save()
            with language(new_user.language):
                Notification.build(
                    type_=Notification.TYPE.INFO,
                    sender=None,
                    recipient=new_user,
                    header=_('%(name)s welcome to Resouce Hub!') % {
                        'name': new_user.first_name
                    },
                    message='',
                    link='',
                    level=Notification.LEVEL.LOW,
                    target=new_user,
                )
                send_verification_mail(new_user, request)
            login(request, new_user)

            message = _(
                'Welcome to Resource Hub!')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:home'))

        return render(request, 'core/register.html', user_form.get_forms())


class Verify(View):
    def get(self, request, uidb64, token):
        token_generator = TokenGenerator()
        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except(TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None
        if user is not None and token_generator.check_token(user, token):
            with transaction.atomic():
                user.is_verified = True
                user.save()

            message = _('Your account has been verified successfully.')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:home'))

        message = _('Your verification-link is invalid!')
        messages.add_message(request, messages.ERROR, message)
        return redirect(reverse('core:login'))


class VerificationResend(View):
    template_name = 'core/control/account_verification_resend.html'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        send_verification_mail(self.request.user, request)
        return redirect(reverse('control:account_verification_resend'))


def custom_login(request):
    if request.user.is_authenticated:
        return redirect(reverse('control:home'))

    return LoginView.as_view(
        template_name='core/login.html')(request)


@method_decorator(login_required, name='dispatch')
class SetRole(View):
    def post(self, request):
        user = request.user
        role_change_form = RoleChangeForm(user, request.POST)

        if role_change_form.is_valid():
            role_change_form.save(request)
        else:
            messages.add_message(request, messages.ERROR,
                                 role_change_form.errors)
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
