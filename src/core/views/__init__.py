from smtplib import SMTPException

from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.db import transaction
from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt

from core.decorators import organization_admin_required
from core.forms import *
from core.models import *
from core.tables import OrganizationsTable, MembersTable, LocationsTable
from core.tokens import TokenGenerator
from core.jobs import send_mail


def index(request):
    return redirect(reverse('core:home'))


class Home(View):
    def get(self, request):
        context = {'userform': ActorForm()}
        return render(request, 'core/home.html', context)


class Support(View):
    template_name = 'core/support.html'
    context = {
        'issue_form': ReportIssueForm(),
    }

    def get(self, request):
        return render(request, self.template_name, self.context)

    def post(self, request):
        issue_form = ReportIssueForm(request.POST)

        if issue_form.is_valid():
            try:
                issue_form.post()
                message = _('Your issue has been posted!')
                messages.add_message(request, messages.SUCCESS, message)
            except IOError:
                message = _('Your issue could not be posted!')
                messages.add_message(request, messages.ERROR, message)
                self.context['issue_form'] = issue_form
                return render(request, self.template_name, self.context)

            return redirect(reverse('core:support'))
        else:
            self.context['issue_form'] = issue_form
            return render(request, self.template_name, self.context)


class Language(View):
    def get(self, request):
        return render(request, 'core/language.html')


@method_decorator(xframe_options_exempt, name='dispatch')
class Register(View):
    template_name = 'core/register.html'

    @xframe_options_exempt
    def get(self, request):
        if request.user.is_authenticated:
            message = _('You are already logged in.')
            messages.add_message(request, messages.INFO, message)
            return redirect(reverse('admin:home'))
        else:
            user_form = UserFormManager()
            return render(request, 'core/register.html', user_form.get_forms())

    def post(self, request):
        user_form = UserFormManager(request)

        if (user_form.is_valid()):
            with transaction.atomic():
                new_user = user_form.save()
                new_user.is_active = False
                new_user.save()

            current_site = get_current_site(request)
            subject = _('Activate your account')
            token_generator = TokenGenerator()

            message = render_to_string('core/mail_activation.html', context={
                'user': new_user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
                'token': token_generator.make_token(new_user),
            })

            recipient = new_user.email
            send_mail.delay(subject, message, [recipient])

            message = _(
                'Please confirm your email address to complete the registration')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('core:login'))

        else:
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
            user.is_active = True
            user.save()
            login(request, user)
            message = _('Your account has been activated successfully.')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('admin:home'))
        else:
            message = _('Your activation-link is invalid!')
            messages.add_message(request, messages.ERROR, message)
            return redirect(reverse('core:login'))


def custom_login(request):
    if request.user.is_authenticated:
        return redirect(reverse('admin:home'))
    else:
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


# Internal admin section
@method_decorator(login_required, name='dispatch')
class Admin(View):
    def get(self, request):
        return render(request, 'core/admin/index.html')


class ScopeView(View):
    legal_scope = []

    def scope_is_valid(self, scope):
        return scope in self.legal_scope

    def dispatch(self, *args, **kwargs):
        if self.scope_is_valid(kwargs['scope']):
            return super(ScopeView, self).dispatch(*args, **kwargs)
        else:
            raise Http404


@method_decorator(login_required, name='dispatch')
class AccountSettings(ScopeView):
    template_name = 'core/admin/account_settings.html'
    legal_scope = ['email', 'password', ]

    def get(self, request, scope):
        account_form = UserAccountFormManager(request)
        return render(request, self.template_name, account_form.get_forms(scope))

    def post(self, request, scope):
        account_form = UserAccountFormManager(request)

        if scope == 'email':
            account_form.change_email()
            message = _('Your email has been updated successfully.')
        elif scope == 'password':
            account_form.change_password()
            message = _('Your password has been updated successfully.')

        if account_form.is_valid:
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('admin:account_settings', kwargs={'scope': scope}))
        else:
            return render(request, self.template_name, account_form.get_forms(scope))


@method_decorator(login_required, name='dispatch')
class AccountProfile(ScopeView):
    template_name = 'core/admin/account_profile.html'
    redirect_url = 'admin:account_profile'
    legal_scope = ['info', 'address', 'bank_account', ]

    def get(self, request, scope):
        profile_form = ProfileFormManager(request, request.user)
        return render(request, self.template_name, profile_form.get_forms(scope))

    def post(self, request, scope):
        profile_form = ProfileFormManager(request, request.user)
        if scope == 'info':
            profile_form.change_info()
            message = _('Your info has been updated')
        elif scope == 'address':
            profile_form.change_address()
            message = _('Your address has been updated')
        elif scope == 'bank_account':
            profile_form.change_bank_account()
            message = _('Your bank account has been updated')

        if profile_form.is_valid:
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse(self.redirect_url, kwargs={'scope': scope}))
        else:
            return render(request, self.template_name, profile_form.get_forms(scope))


@method_decorator(login_required, name='dispatch')
class OrganizationsManage(View):
    def get(self, request):
        user = request.user
        organizations = Organization.objects.all().filter(members__pk=user.id)

        if organizations:
            data = []
            for o in organizations:
                role = OrganizationMember.get_role(user, o)
                data.append({
                    'name': o.name,
                    'role': role,
                    'organization_id': o.id,
                })
            organizations_table = OrganizationsTable(data)
        else:
            organizations_table = None

        context = {
            'organizations_table': organizations_table,
        }
        return render(request, 'core/admin/organizations_manage.html', context)


@method_decorator(login_required, name='dispatch')
class OrganizationCreate(View):
    template_name = 'core/admin/organizations_create.html'

    def get(self, request):
        organization_form = OrganizationFormManager()
        return render(request, self.template_name, organization_form.get_forms())

    def post(self, request):
        organization_form = OrganizationFormManager(request)

        if organization_form.is_valid():
            with transaction.atomic():
                organization_form.save()
            message = _('The organization has been registered')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('admin:organizations_manage'))
        else:
            return render(request, self.template_name, organization_form.get_forms())


@method_decorator(login_required, name='dispatch')
class OrganizationsProfile(View):
    def get(self, request, organization_id):
        user = request.user
        organization = get_object_or_404(Actor, pk=organization_id)
        member = get_object_or_404(
            OrganizationMember, organization__id=organization_id, user=user)

        context = {
            'organization': organization,
            'is_admin': member.is_admin(),
        }

        return render(request, 'core/admin/organizations_profile.html', context)


@method_decorator([login_required, organization_admin_required], name='dispatch')
class OrganizationProfileEdit(View):
    template_name = 'core/admin/organizations_profile_edit.html'
    redirect_url = 'admin:organizations_profile_edit'
    legal_scope = ['info', 'address', 'bank_account']

    def get(self, request, organization_id, scope):
        organization = get_object_or_404(Organization, pk=organization_id)
        profile_form = ProfileFormManager(request, organization)
        context = profile_form.get_forms(scope)
        context['organization'] = organization
        return render(request, self.template_name, context)

    def post(self, request, organization_id, scope):
        organization = get_object_or_404(Organization, pk=organization_id)
        profile_form = ProfileFormManager(request, organization)
        if scope == 'info':
            profile_form.change_info()
            message = _('Your info has been updated')
        elif scope == 'address':
            profile_form.change_address()
            message = _('Your address has been updated')
        elif scope == 'bank_account':
            profile_form.change_bank_account()
            message = _('Your bank account has been updated')

        if profile_form.is_valid:
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse(self.redirect_url, kwargs={'organization_id': organization_id,
                                                               'scope': scope}))
        else:
            return render(request, self.template_name, profile_form.get_forms(scope))


@method_decorator([login_required, organization_admin_required], name='dispatch')
class OrganizationMembers(View):
    def get(self, request, organization_id):
        user = request.user
        organization = get_object_or_404(Organization, pk=organization_id)
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


@method_decorator([login_required, organization_admin_required], name='dispatch')
class OrganizationMembersAdd(View):
    template_name = 'core/admin/organizations_members_add.html'

    def get(self, request, organization_id):
        organization = get_object_or_404(Organization, pk=organization_id)
        member_add_form = OrganizationMemberAddForm(organization=organization)

        context = {
            'member_add_form': member_add_form,
            'organization': organization,
        }
        return render(request, self.template_name, context)

    def post(self, request, organization_id):
        organization = get_object_or_404(Organization, pk=organization_id)
        member_add_form = OrganizationMemberAddForm(organization,
                                                    request.POST)
        if member_add_form.is_valid():
            member_add_form.save()

            message = _('User has been added to ' + organization.name)
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('admin:organizations_members', kwargs={'organization_id': organization_id}))
        else:
            context = {
                'member_add_form': member_add_form,
                'organization': organization,
            }
            return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class LocationCreate(View):
    def get(self, request):
        location_form = LocationForm()
        address_form = AddressForm()
        context = {
            'location_form': location_form,
            'address_form': address_form,
        }
        return render(request, 'core/admin/locations_create.html', context)

    def post(self, request):
        location_form = LocationForm(request.POST)
        address_form = AddressForm(request.POST)

        if address_form.is_valid():
            new_address = address_form.save()
            if location_form.is_valid():
                owner = request.actor
                new_location = location_form.save(owner, commit=False)
                new_location.address = new_address
                new_location.save()

                message = _('The location has been created')
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('admin:locations_manage'))

        context = {
            'location_form': location_form,
            'address_form': address_form,
        }
        return render(request, 'core/admin/locations_create.html', context)


@method_decorator(login_required, name='dispatch')
class LocationManage(View):
    def get(self, request):
        locations = Location.objects.all()

        if locations:
            data = []
            for l in locations:
                data.append({
                    'name': l.name,
                    'id': l.id,
                })
            locations_table = LocationsTable(data)
        else:
            locations_table = None

        context = {
            'locations_table': locations_table,
        }
        return render(request, 'core/admin/locations_manage.html', context)
