from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Q
from django.forms import Form
from django.http import Http404, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import View

from ..decorators import organization_admin_required
from ..forms import *
from ..models import *
from ..signals import register_contract_procedures, register_payment_methods
from ..tables import (ContractProcedureTable, LocationsTable, MembersTable,
                      OrganizationsTable, PaymentMethodsTable)
from ..utils import get_associated_objects
from . import TableView


@method_decorator(login_required, name='dispatch')
class Home(View):
    def get(self, request):
        return render(request, 'core/control/index.html')


class ScopeView(View):
    legal_scope = []

    def scope_is_valid(self, scope):
        return scope in self.legal_scope

    def dispatch(self, *args, **kwargs):
        if self.scope_is_valid(kwargs['scope']):
            return super(ScopeView, self).dispatch(*args, **kwargs)
        raise Http404


@method_decorator(login_required, name='dispatch')
class AccountSettings(ScopeView):
    template_name = 'core/control/account_settings.html'
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
            return redirect(reverse('control:account_settings', kwargs={'scope': scope}))
        else:
            return render(request, self.template_name, account_form.get_forms(scope))


@method_decorator(login_required, name='dispatch')
class AccountProfile(ScopeView):
    template_name = 'core/control/account_profile.html'
    redirect_url = 'control:account_profile'
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
class FinanceBankAccounts(View):
    def get(self, request):
        return render(request, 'core/control/finance_bank_accounts.html')


@method_decorator(login_required, name='dispatch')
class FinancePaymentMethodsManage(TableView):
    header = _('Payment methods')

    def get_queryset(self):
        methods = get_associated_objects(
            self.request.actor,
            PaymentMethod
        ).select_subclasses()

        result = []
        for method in methods:
            result.append(
                {
                    'pk': method.pk,
                    'name': method.name,
                    'owner': method.owner,
                    'method_type': method.verbose_name,
                }
            )
        return result

    def get_table(self):
        return PaymentMethodsTable


def get_subobject_or_404(klass, *args, **kwargs):
    try:
        return klass.objects.get_subclass(*args, **kwargs)
    except klass.DoesNotExist:
        raise Http404('No %s matches the given query.')


@method_decorator(login_required, name='dispatch')
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

    def get(self, request):
        context = {
            'payment_methods': self.get_payment_methods(),
        }
        return render(request, self.template_name, context)

    def post(self, request):
        payment_methods = self.get_payment_methods(data=request.POST)
        for payment_method in payment_methods:
            form = payment_method['form']
            if form.is_valid():
                form.save(request=request)
                message = _('The configuration for {} has been saved'.format(
                    str(payment_method['name'])
                ))
                messages.add_message(request, messages.SUCCESS, message)
                return redirect(reverse('control:finance_payment_methods_add'))
        context = {
            'payment_methods': payment_methods,
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
            return HttpResponseForbidden

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

        contract.payment_method = PaymentMethod.objects.get_subclass(
            pk=contract.payment_method.pk)

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
                contract.set_canceled(request)
                message = _('{} has been canceled'.format(
                    contract.verbose_name))
            elif choice == 'confirm':
                contract.set_waiting(request)
                message = _('{} has been confirmed'.format(
                    contract.verbose_name))
            else:
                message = _('Invalid Choice')
        else:
            if choice == 'decline':
                contract.set_declined(request)
                message = _('{} has been decline'.format(
                    contract.verbose_name))
            elif choice == 'accept':
                contract.set_running(request)
                message = _('{} has been accepted'.format(
                    contract.verbose_name))
            else:
                message = _('Invalid Choice')

        messages.add_message(request, messages.SUCCESS, message)
        return redirect(reverse('control:finance_contracts_manage'))


@method_decorator(login_required, name='dispatch')
class FinanceContractProceduresManage(TableView):
    header = _('Manage contract procedures')

    def get_queryset(self):
        return get_associated_objects(
            self.request.actor,
            ContractProcedure
        ).select_subclasses()

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
class Notifications(View):
    template_name = 'core/control/notifications.html'

    def get(self, request):
        return render(request, self.template_name)


@method_decorator(login_required, name='dispatch')
class OrganizationsManage(TableView):
    header = _('Manage your organizations')

    def get_table(self):
        return OrganizationsTable

    def get_queryset(self):
        user = self.request.user
        query = Q(members=user)
        query.add(
            Q(organizationmember__role__gte=OrganizationMember.MEMBER), Q.AND)
        return Organization.objects.filter(query).annotate(role=F('organizationmember__role')).values(
            'id', 'name', 'role')


@method_decorator(login_required, name='dispatch')
class OrganizationsCreate(View):
    template_name = 'core/control/organizations_create.html'

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
class OrganizationsMembers(View):
    def get(self, request, organization_id):
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
        return render(request, 'core/control/organizations_members.html', context)


@method_decorator([login_required, organization_admin_required], name='dispatch')
class OrganizationsMembersAdd(View):
    template_name = 'core/control/organizations_members_add.html'

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
            return redirect(reverse('control:organizations_members', kwargs={'organization_id': organization_id}))
        else:
            context = {
                'member_add_form': member_add_form,
                'organization': organization,
            }
            return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class LocationsCreate(View):
    def get(self, request):
        location_form = LocationFormManager()
        return render(request, 'core/control/locations_create.html', location_form.get_forms())

    def post(self, request):
        location_form = LocationFormManager(request)

        if location_form.is_valid():
            location_form.save()

            message = _('The location has been created')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:locations_manage'))

        return render(request, 'core/control/locations_create.html', location_form.get_forms())


@method_decorator(login_required, name='dispatch')
class LocationsManage(TableView):
    header = _('Manage locations')

    def get_queryset(self):
        return get_associated_objects(
            self.request.actor,
            Location
        )

    def get_table(self):
        return LocationsTable


@method_decorator(login_required, name='dispatch')
class LocationsProfileEdit(View):
    template_name = 'core/control/locations_profile_edit.html'

    def get(self, request, location_id):
        location = get_object_or_404(Location, pk=location_id)
        location_form = LocationFormManager(
            instances={
                'location_form': location,
                'address_form': location.address,
            }
        )
        return render(request, self.template_name, location_form.get_forms())

    def post(self, request, location_id):
        location = get_object_or_404(Location, pk=location_id)
        location_form = LocationFormManager(
            request=request,
            instances={
                'location_form': location,
                'address_form': location.address,
            }
        )

        if location_form.is_valid():
            location_form.save()
            return redirect(reverse('control:locations_profile_edit', kwargs={'location_id': location_id}))

        return render(request, self.template_name, location_form.get_forms())
