from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import View

from resource_hub.core.utils import get_associated_objects
from resource_hub.core.views import TableView

from .forms import (VenueContractFormManager,
                    VenueContractProcedureFormManager, VenueForm)
from .models import Venue, VenueContractProcedure
from .tables import VenuesTable

TTL = 60 * 5


# @cache_page(TTL)
def index(request):
    return render(request, 'venues/index.html')

# Admin section
@method_decorator(login_required, name='dispatch')
class VenuesManage(TableView):
    header = _('Manage venues')

    def get_queryset(self):
        return get_associated_objects(
            self.request.actor,
            Venue
        )

    def get_table(self):
        return VenuesTable


@method_decorator(login_required, name='dispatch')
class VenuesCreate(View):
    def get(self, request):
        venue_form = VenueForm(request)
        context = {
            'venue_form': venue_form,
        }
        return render(request, 'venues/control/venues_create.html', context)

    def post(self, request):
        venue_form = VenueForm(request, data=request.POST, files=request.FILES)

        if venue_form.is_valid():
            venue_form.save()

            message = ('The venue has been created')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:venues_manage'))

        context = {
            'venue_form': venue_form,
        }
        return render(request, 'venues/control/venues_create.html', context)


@method_decorator(login_required, name='dispatch')
class VenuesProfileEdit(View):
    template_name = 'venues/control/venues_profile_edit.html'

    def get(self, request, venue_id):
        venue = get_object_or_404(Venue, pk=venue_id)
        venue_form = VenueForm(request, instance=venue)
        context = {
            'venue_form': venue_form,
        }
        return render(request, self.template_name, context)

    def post(self, request, venue_id):
        venue = get_object_or_404(Venue, pk=venue_id)
        venue_form = VenueForm(
            request,
            instance=venue,
        )

        if venue_form.is_valid():
            venue_form.save()
            message = _('The venue has been updated')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:venues_profile_edit', kwargs={'venue_id': venue_id}))

        context = {
            'venue_form': venue_form,
        }
        return render(request, self.template_name, context)


class VenuesDetails(View):
    def get(self, request, location_slug, venue_slug):
        venue = get_object_or_404(
            Venue, slug=venue_slug, location__slug=location_slug)
        context = {'venue': venue}
        return render(request, 'venues/venue_details.html', context)


@method_decorator(login_required, name='dispatch')
class EventsCreate(View):
    template_name = 'venues/venue_events_create.html'

    def get(self, request, location_slug, venue_slug):
        venue = get_object_or_404(
            Venue, slug=venue_slug, location__slug=location_slug)
        context = VenueContractFormManager(venue, request).get_forms()
        context['venue'] = venue
        return render(request, self.template_name, context)

    def post(self, request, location_slug, venue_slug):
        venue = get_object_or_404(
            Venue, slug=venue_slug, location__slug=location_slug)
        venue_contract_form = VenueContractFormManager(venue, request)
        if venue_contract_form.is_valid():
            with transaction.atomic():
                venue_contract = venue_contract_form.save()
            venue_contract.set_pending(
                occurrences=venue_contract_form.occurrences)
            message = _(
                'The event has been created successfully. You can review it and either confirm or cancel.')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_contracts_manage_details', kwargs={'pk': venue_contract.pk}))
        return render(request, self.template_name, venue_contract_form.get_forms())


@method_decorator(login_required, name='dispatch')
class EventsManageDetails(View):
    def get(self, request, event):
        return


@method_decorator(login_required, name='dispatch')
class ContractProceduresCreate(View):
    template_name = 'venues/control/contract_procedures_create.html'

    def get(self, request):
        contract_procedure_form = VenueContractProcedureFormManager(request)
        return render(request, self.template_name, contract_procedure_form.get_forms())

    def post(self, request):
        contract_procedure_form = VenueContractProcedureFormManager(request)

        if contract_procedure_form.is_valid():
            contract_procedure_form.save()
            message = _(
                'The event contract procedure has been saved successfully')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_contract_procedures_manage'))
        return render(request, self.template_name, contract_procedure_form.get_forms())


@method_decorator(login_required, name='dispatch')
class ContractProceduresEdit(View):
    template_name = 'venues/control/contract_procedures_edit.html'

    def get(self, request, pk):
        contract_procedure = get_object_or_404(VenueContractProcedure, pk=pk)
        contract_procedure_form = VenueContractProcedureFormManager(
            request, instance=contract_procedure)
        return render(request, self.template_name, contract_procedure_form.get_forms())

    def post(self, request, pk):
        contract_procedure = get_object_or_404(VenueContractProcedure, pk=pk)
        contract_procedure_form = VenueContractProcedureFormManager(
            request, instance=contract_procedure)

        if contract_procedure_form.is_valid():
            contract_procedure_form.save()

            message = _('The changes have been saved')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_contract_procedures_manage'))
        return render(request, self.template_name, contract_procedure_form.get_forms())
