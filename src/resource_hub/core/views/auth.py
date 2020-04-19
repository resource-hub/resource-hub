
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
from django.utils.translation import ugettext_lazy as _
from django.views import View

from resource_hub.core.forms import RoleChangeForm, UserFormManager
from resource_hub.core.jobs import notify, send_mail
from resource_hub.core.models import Notification, User
from resource_hub.core.tokens import TokenGenerator


class Register(View):
    template_name = 'core/register.html'

    def get(self, request):
        if request.user.is_authenticated:
            message = _('You are already logged in.')
            messages.add_message(request, messages.INFO, message)
            return redirect(reverse('control:home'))

        user_form = UserFormManager()
        return render(request, 'core/register.html', user_form.get_forms())

    def post(self, request):
        user_form = UserFormManager(request)

        if (user_form.is_valid()):
            with transaction.atomic():
                new_user = user_form.save()

            current_site = get_current_site(request)
            subject = _('Activate your account')
            token_generator = TokenGenerator()

            message = render_to_string('core/mail_activation.html', context={
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': token_generator.make_token(new_user),
            })
            notify.delay(
                Notification.TYPE.INFO,
                sender=None,
                action='',
                target='',
                link='',
                recipient=new_user,
                level=Notification.LEVEL.LOW,
                message=_('%(name)s, welcome to Resouce Hub!') % {
                    'name': new_user.first_name}
            )

            recipient = new_user.email
            send_mail.delay(subject, message, [recipient])
            login(request, new_user)

            message = _(
                'Please confirm your email address to complete the registration')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:home'))

        return render(request, 'core/register.html', user_form.get_forms())


class Activate(View):
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

            message = _('Your account has been activated successfully.')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:home'))

        message = _('Your activation-link is invalid!')
        messages.add_message(request, messages.ERROR, message)
        return redirect(reverse('core:login'))


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
