from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import F, Q
from django.db.models.query import QuerySet
from django.forms import Form
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django.views import View

from ..decorators import organization_admin_required, owner_required
from ..forms import *
from ..forms import OrganizationInvitationFormManager, PaymentMethodFilterForm
from ..models import *
from ..signals import register_contract_procedures, register_payment_methods
from ..tables import (ContractProcedureTable, InvoiceTable, LocationsTable,
                      MembersTable, OrganizationsTable, PaymentMethodsTable)
from . import TableView


@method_decorator(login_required, name='dispatch')
class Home(View):
    def get(self, request):
        return render(request, 'core/control/index.html')


class ScopeView(View):
    legal_scope = []

    def scope_is_valid(self, scope):
        if '*' in self.legal_scope:
            return True
        return scope in self.legal_scope

    def dispatch(self, *args, **kwargs):
        if self.scope_is_valid(kwargs['scope']):
            return super(ScopeView, self).dispatch(*args, **kwargs)
        raise Http404


@method_decorator(login_required, name='dispatch')
class AccountSecurity(ScopeView):
    template_name = 'core/control/account_security.html'
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
            return redirect(reverse('control:account_security', kwargs={'scope': scope}))
        return render(request, self.template_name, account_form.get_forms(scope))


@method_decorator(login_required, name='dispatch')
class AccountSettings(ScopeView):
    template_name = 'core/control/account_settings.html'
    redirect_url = 'control:account_settings'
    legal_scope = ['info', 'address', 'bank_account', 'invoicing_settings', ]

    def get(self, request, scope):
        profile_form = ProfileFormManager(request, request.actor)
        return render(request, self.template_name, profile_form.get_forms(scope))

    def post(self, request, scope):
        profile_form = ProfileFormManager(request, request.actor)
        if scope == 'info':
            profile_form.change_info()
            message = _('Your info has been updated')
        elif scope == 'address':
            profile_form.change_address()
            message = _('Your address has been updated')
        elif scope == 'bank_account':
            profile_form.change_bank_account()
            message = _('Your bank account has been updated')
        elif scope == 'invoicing_settings':
            profile_form.change_invoicing_settings()
            message = _('Your bank invoicing settings have been updated')

        if profile_form.is_valid:
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse(self.redirect_url, kwargs={'scope': scope}))
        return render(request, self.template_name, profile_form.get_forms(scope))


@method_decorator(login_required, name='dispatch')
class FinanceBankAccounts(View):
    def get(self, request):
        return render(request, 'core/control/finance_bank_accounts.html')


@method_decorator(login_required, name='dispatch')
class FinancePaymentMethodsManage(TableView):
    header = _('Payment methods')
    class_ = PaymentMethod
    subclasses = True

    def get_filters(self, request):
        return {
            'owner': {
                'value': request.actor,
                'connector': Q.AND,
            }
        }

    def get_filter_form(self, request, data):
        return PaymentMethodFilterForm(data=data)

    def get_table(self):
        return PaymentMethodsTable


def get_subobject_or_404(klass, *args, **kwargs):
    try:
        return klass.objects.get_subclass(*args, **kwargs)
    except klass.DoesNotExist:
        raise Http404('No %s matches the given query.')


@method_decorator(login_required, name='dispatch')
@method_decorator(owner_required, name='dispatch')
class FinancePaymentMethodsEdit(View):
    template_name = 'core/control/finance_payment_methods_edit.html'

    def get(self, request, pk):
        payment_method = get_subobject_or_404(PaymentMethod, pk=pk)
        context = {
            'form': payment_method.form(instance=payment_method)
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        payment_method = get_subobject_or_404(PaymentMethod, pk=pk)
        form = payment_method.form(request.POST, instance=payment_method)
        if form.is_valid():
            form.save(request)
            message = _('Your changes have been saved successfully')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_payment_methods_manage'))

        context = {
            'form': form
        }
        return render(request, self.template_name, context)

    @classmethod
    def get_resource(cls):
        return PaymentMethod


@method_decorator(login_required, name='dispatch')
class FinancePaymentMethodsAdd(View):
    template_name = 'core/control/finance_payment_methods_add.html'

    def get_payment_methods(self, data=None):
        payment_methods = register_payment_methods.send(sender=self.__class__)
        payment_methods_list = []

        for method in payment_methods:
            method = method[1]
            payment_methods_list.append(
                {
                    'name': method.verbose_name,
                    'form': method.form(data=data, prefix=method.prefix),
                    'prefix': method.prefix,
                }
            )
        return payment_methods_list

    def get(self, request, scope):
        payment_methods = self.get_payment_methods()
        context = {
            'payment_methods': payment_methods,
            'scope': scope,
        }
        return render(request, self.template_name, context)

    def post(self, request, scope):
        payment_methods = self.get_payment_methods(data=request.POST)
        for payment_method in payment_methods:
            form = payment_method['form']
            if form.is_valid():
                form.save(request=request)
                message = _('The configuration for {} has been saved'.format(
                    str(payment_method['name'])
                ))
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('control:finance_payment_methods_add', kwargs={'scope': payment_method['prefix']}))
        context = {
            'payment_methods': payment_methods,
            'scope': scope,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class FinanceContractsCredited(View):
    def get(self, request):
        return render(request, 'core/control/finance_contracts_credited.html')


class FinanceContractsDebited(View):
    def get(self, request):
        return render(request, 'core/control/finance_contracts_debited.html')


@method_decorator(login_required, name='dispatch')
class FinanceContractsManageDetails(View):
    template_name = 'core/control/finance_contracts_manage_details.html'

    def get(self, request, pk):
        contract = get_subobject_or_404(Contract, pk=pk)
        actor = request.actor
        if contract.debitor == actor:
            is_debitor = True
        elif contract.creditor == actor:
            is_debitor = False
        else:
            raise PermissionDenied('Actor has to be debitor or creditor!')

        timer = None
        if contract.is_pending and is_debitor:
            delta = (timedelta(
                minutes=contract.expiration_period) - (timezone.now() - contract.created_at))

            # double check in case scheduler hasnt updated the state
            if delta.total_seconds() <= 0:
                contract.set_expired()
            else:
                diff = delta.seconds
                hours, remainder = divmod(diff, 3600)
                minutes, seconds = divmod(remainder, 60)
                timer = '{0:02d}:{1:02d}:{2:02d}'.format(
                    hours, minutes, seconds)
        if contract.payment_method:
            contract.payment_method = PaymentMethod.objects.get_subclass(
                pk=contract.payment_method.pk)

        if (contract.is_pending or contract.is_waiting) and contract.claim_set.filter(period_start__lt=timezone.now()).exists():
            message = _('This contract contains claims that are in the past')
            messages.add_message(request, messages.WARNING, message)

        context = {
            'contract': contract,
            'is_debitor': is_debitor,
            'timer': timer,
        }
        return render(request, self.template_name, context)

    def post(self, request, pk):
        contract = get_subobject_or_404(Contract, pk=pk)
        actor = request.actor

        choice = request.POST.get('choice', None)
        if contract.debitor == actor:
            is_debitor = True
        elif contract.creditor == actor:
            is_debitor = False
        else:
            return HttpResponseForbidden

        if is_debitor:
            if choice == 'cancel':
                with transaction.atomic():
                    contract.set_cancelled()
                message = _('%(contract)s has been canceled') % {
                    'contract': contract.verbose_name}
            elif choice == 'confirm':
                with transaction.atomic():
                    if contract.payment_method.is_prepayment:
                        return get_subobject_or_404(PaymentMethod, pk=contract.payment_method.pk).initialize(contract, request)
                    contract.set_waiting(request)
                message = _('%(contract)s has been confirmed') % {
                    'contract': contract.verbose_name}
            else:
                message = _('Invalid Choice')
        else:
            if choice == 'decline':
                with transaction.atomic():
                    contract.set_declined(request)
                message = _('%(contract)s has been declined') % {
                    'contract': contract.verbose_name}
            elif choice == 'accept':
                with transaction.atomic():
                    contract.set_running(request)
                message = _('%(contract)s has been accepted') % {
                    'contract': contract.verbose_name}
            else:
                message = _('Invalid Choice')

        if choice == 'terminate':
            with transaction.atomic():
                contract.set_terminated(actor)
            message = _('%(contract)s has been terminated') % {
                'contract': contract.verbose_name}

        messages.add_message(request, messages.SUCCESS, message)
        return redirect(reverse('control:finance_contracts_manage_details', kwargs={'pk': pk}))


@method_decorator(login_required, name='dispatch')
class FinanceContractProceduresManage(TableView):
    header = _('Manage contract procedures')
    class_ = ContractProcedure
    subclasses = True

    def get_filters(self, request):
        return {
            'owner': {
                'value': request.actor,
                'connector': Q.AND,
            }
        }

    def get_table(self):
        return ContractProcedureTable


@method_decorator(login_required, name='dispatch')
class FinanceContractProceduresCreate(View):
    def get(self, request):
        contract_procedures = register_contract_procedures.send(
            sender=self.__class__)
        if contract_procedures:
            contract_procedures = list(
                map(lambda x: x[1], contract_procedures))
        context = {
            'contract_procedures': contract_procedures
        }
        return render(request, 'core/control/finance_contract_procedures_create.html', context)


@method_decorator(login_required, name='dispatch')
class FinanceInvoicesOutgoing(TableView):
    header = _('Outgoing invoices')
    class_ = Invoice
    filters = False
    actions = False

    def get_filters(self, request):
        return {
            'contract__creditor': {
                'value': request.actor,
                'connector': Q.AND,
            }
        }

    def get_table(self):
        return InvoiceTable


@method_decorator(login_required, name='dispatch')
class FinanceInvoicesIncoming(TableView):
    header = _('Incoming invoices')
    class_ = Invoice
    filters = False
    actions = False

    def get_filters(self, request):
        return {
            'contract__debitor': {
                'value': request.actor,
                'connector': Q.AND,
            }
        }

    def get_table(self):
        return InvoiceTable


@method_decorator(login_required, name='dispatch')
class Notifications(View):
    template_name = 'core/control/notifications.html'

    def get(self, request):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
class NotificationsSettings(View):
    template_name = 'core/control/notifications_settings.html'

    def get(self, request):
        notifications_form = NotificationsSettingsFormManager(
            request.user,
            request.actor,
            instances=request.actor,
        )
        return render(request, self.template_name, notifications_form.get_forms())

    def post(self, request):
        notifications_form = NotificationsSettingsFormManager(
            request.user,
            request.actor,
            data=request.POST,
            files=request.FILES,
            instances=request.actor,
        )

        if notifications_form.is_valid():
            with transaction.atomic():
                notifications_form.save()
            message = _('The settings have been saved')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:notifications_settings'))
        return render(request, self.template_name, notifications_form.get_forms())


@method_decorator(login_required, name='dispatch')
class OrganizationsManage(TableView):
    header = _('Manage your organizations')
    class_ = Organization

    def get_table(self):
        return OrganizationsTable

    def get_functions(self, request):
        return {
            'annotate': {
                'func': QuerySet.annotate,
                'args': [],
                'kwargs': {
                    'role': F('organizationmember__role'),
                },
            }
        }

    def get_filters(self, request):
        return {
            'members': {
                'value': request.user,
                'connector': Q.AND,
            },
            'organizationmember__role__gte': {
                'value': OrganizationMember.MEMBER,
                'connector': Q.AND,
            },
        }


@method_decorator(login_required, name='dispatch')
class OrganizationsCreate(View):
    template_name = 'core/control/organizations_create.html'

    def get(self, request):
        organization_form = OrganizationFormManager(
            request.user, request.actor)
        return render(request, self.template_name, organization_form.get_forms())

    def post(self, request):
        organization_form = OrganizationFormManager(
            request.user, request.actor, data=request.POST, files=request.FILES)

        if organization_form.is_valid():
            with transaction.atomic():
                organization_form.save()
            message = _('The organization has been registered')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:organizations_manage'))

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

        return render(request, 'core/control/organizations_profile.html', context)


@method_decorator([login_required, organization_admin_required], name='dispatch')
class OrganizationsProfileEdit(View):
    template_name = 'core/control/organizations_profile_edit.html'
    redirect_url = 'control:organizations_profile_edit'
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
        return render(request, self.template_name, profile_form.get_forms(scope))


@method_decorator([login_required, organization_admin_required], name='dispatch')
class OrganizationsMembers(TableView):
    organization = None
    template_name = 'core/control/organizations_members.html'
    class_ = OrganizationMember

    def get_filters(self, request):
        return {
            'organization': {
                'value': self.organization,
                'connector': Q.AND,
            }
        }

    def get_table(self):
        return MembersTable

    def get(self, request, organization_id):
        self.organization = get_object_or_404(Organization, pk=organization_id)
        self.header = self.organization.name
        context = self.get_context(request)
        context['organization'] = self.organization
        return render(request, self.template_name, context)


@method_decorator([login_required, organization_admin_required], name='dispatch')
class OrganizationsMembersAdd(View):
    template_name = 'core/control/organizations_members_add.html'

    def get(self, request, organization_id):
        organization = get_object_or_404(Organization, pk=organization_id)
        invitation_form = OrganizationInvitationFormManager(
            request.user,
            request.actor,
            organization=organization)

        context = {
            **invitation_form.get_forms(),
            'organization': organization,
        }
        return render(request, self.template_name, context)

    def post(self, request, organization_id):
        organization = get_object_or_404(Organization, pk=organization_id)
        invitation_form = OrganizationInvitationFormManager(request.user, request.actor,
                                                            organization=organization,
                                                            data=request.POST)
        if invitation_form.is_valid():
            with transaction.atomic():
                invitation_form.save()

            message = _('User has been added to ' + organization.name)
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:organizations_members', kwargs={'organization_id': organization_id}))
        context = {
            **invitation_form.get_forms(),
            'organization': organization,
        }
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class LocationsCreate(View):
    def get(self, request):
        location_form = LocationFormManager(request.user, request.actor)
        return render(request, 'core/control/locations_create.html', location_form.get_forms())

    def post(self, request):
        location_form = LocationFormManager(
            request.user, request.actor, data=request.POST, files=request.FILES)

        if location_form.is_valid():
            location_form.save()

            message = _('The location has been created')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:locations_manage'))

        return render(request, 'core/control/locations_create.html', location_form.get_forms())


@method_decorator(login_required, name='dispatch')
class LocationsManage(TableView):
    header = _('Manage locations')
    class_ = Location

    def get_filters(self, request):
        return {
            'owner': {
                'value': request.actor,
                'connector': Q.AND,
            }
        }

    def get_table(self):
        return LocationsTable


@method_decorator(login_required, name='dispatch')
@method_decorator(owner_required, name='dispatch')
class LocationsEdit(View):
    template_name = 'core/control/locations_edit.html'

    @classmethod
    def get_resource(cls):
        return Location

    def get(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        location_form = LocationFormManager(
            request.user,
            request.actor,
            instances={
                'location_form': location,
                'address_form': location.address,
            }
        )
        return render(request, self.template_name, location_form.get_forms())

    def post(self, request, pk):
        location = get_object_or_404(Location, pk=pk)
        location_form = LocationFormManager(
            request.user,
            request.actor,
            data=request.POST,
            files=request.FILES,
            instances={
                'location_form': location,
                'address_form': location.address,
            }
        )

        if location_form.is_valid():
            location_form.save()
            return redirect(reverse('control:locations_edit', kwargs={'pk': pk}))

        return render(request, self.template_name, location_form.get_forms())
