from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View
from resource_hub.core.decorators import owner_required
from resource_hub.core.views import TableView

from .forms import (WorkshopContractFormManager,
                    WorkshopContractProcedureFormManager, WorkshopForm,
                    WorkshopFormManager)
from .models import Workshop, WorkshopContractProcedure
from .tables import WorkshopsTable

TTL = 60 * 5


# @cache_page(TTL)
def index(request):
    return render(request, 'workshops/index.html')
# Admin section


@method_decorator(login_required, name='dispatch')
class WorkshopsManage(TableView):
    header = _('Manage workshops')
    class_ = Workshop

    def get_filters(self, request):
        return {
            'owner': {
                'value': request.actor,
                'connector': Q.AND,
            }
        }

    def get_table(self):
        return WorkshopsTable


@method_decorator(login_required, name='dispatch')
class WorkshopsCreate(View):
    def get(self, request):
        workshop_form = WorkshopFormManager(request.user, request.actor)
        return render(request, 'workshops/control/workshops_create.html', workshop_form.get_forms())

    def post(self, request):
        workshop_form = WorkshopFormManager(
            request.user, request.actor, data=request.POST, files=request.FILES)

        if workshop_form.is_valid():
            with transaction.atomic():
                workshop_form.save()

            message = ('The workshop has been created')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:workshops_manage'))
        return render(request, 'workshops/control/workshops_create.html', workshop_form.get_forms())


@method_decorator(login_required, name='dispatch')
@method_decorator(owner_required, name='dispatch')
class WorkshopsEdit(View):
    template_name = 'workshops/control/workshops_edit.html'

    @classmethod
    def get_resource(cls):
        return Workshop

    def get(self, request, pk):
        workshop = get_object_or_404(Workshop, pk=pk)
        workshop_form = WorkshopFormManager(
            request.user, request.actor, instance=workshop)
        return render(request, self.template_name, workshop_form.get_forms())

    def post(self, request, pk):
        workshop = get_object_or_404(Workshop, pk=pk)
        workshop_form = WorkshopFormManager(
            request.user,
            request.actor,
            data=request.POST,
            files=request.FILES,
            instance=workshop,
        )
        if workshop_form.is_valid():
            workshop_form.save()
            message = _('The workshop has been updated')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:workshops_edit', kwargs={'pk': pk}))

        return render(request, self.template_name, workshop_form.get_forms())


class WorkshopsDetails(View):
    def get(self, request, location_slug, workshop_slug):
        workshop = get_object_or_404(
            Workshop, slug=workshop_slug, location__slug=location_slug)
        context = {'workshop': workshop}
        return render(request, 'workshops/workshop_details.html', context)


@method_decorator(login_required, name='dispatch')
class EventsCreate(View):
    template_name = 'workshops/workshop_events_create.html'

    def get(self, request, location_slug, workshop_slug):
        workshop = get_object_or_404(
            Workshop, slug=workshop_slug, location__slug=location_slug)
        context = WorkshopContractFormManager(workshop, request).get_forms()
        context['workshop'] = workshop
        return render(request, self.template_name, context)

    def post(self, request, location_slug, workshop_slug):
        workshop = get_object_or_404(
            Workshop, slug=workshop_slug, location__slug=location_slug)
        workshop_contract_form = WorkshopContractFormManager(workshop, request)
        if workshop_contract_form.is_valid():
            with transaction.atomic():
                workshop_contract = workshop_contract_form.save()
                workshop_contract.claim_factory(
                    occurrences=workshop_contract_form.occurrences
                )
            message = _(
                'The event has been created successfully. You can review it and either confirm or cancel.')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_contracts_manage_details', kwargs={'pk': workshop_contract.pk}))
        context = WorkshopContractFormManager(workshop, request).get_forms()
        context['workshop'] = workshop
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class EventsManageDetails(View):
    def get(self, request, event):
        return


@method_decorator(login_required, name='dispatch')
class ContractProceduresCreate(View):
    template_name = 'workshops/control/contract_procedures_create.html'

    def get(self, request):
        contract_procedure_form = WorkshopContractProcedureFormManager(request)
        return render(request, self.template_name, contract_procedure_form.get_forms())

    def post(self, request):
        contract_procedure_form = WorkshopContractProcedureFormManager(request)

        if contract_procedure_form.is_valid():
            contract_procedure_form.save()
            message = _(
                'The event contract procedure has been saved successfully')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_contract_procedures_manage'))
        return render(request, self.template_name, contract_procedure_form.get_forms())


@method_decorator(login_required, name='dispatch')
@method_decorator(owner_required, name='dispatch')
class ContractProceduresEdit(View):
    template_name = 'workshops/control/contract_procedures_edit.html'

    @classmethod
    def get_resource(cls):
        return WorkshopContractProcedure

    def get(self, request, pk):
        contract_procedure = get_object_or_404(
            WorkshopContractProcedure, pk=pk)
        contract_procedure_form = WorkshopContractProcedureFormManager(
            request, instance=contract_procedure)
        return render(request, self.template_name, contract_procedure_form.get_forms())

    def post(self, request, pk):
        contract_procedure = get_object_or_404(
            WorkshopContractProcedure, pk=pk)
        contract_procedure_form = WorkshopContractProcedureFormManager(
            request, instance=contract_procedure)

        if contract_procedure_form.is_valid():
            contract_procedure_form.save()

            message = _('The changes have been saved')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_contract_procedures_manage'))
        return render(request, self.template_name, contract_procedure_form.get_forms())
