from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.forms import model_to_dict
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.decorators.cache import cache_page

from resource_hub.core.models import OrganizationMember
from resource_hub.venues.forms import (VenueContractFormManager, VenueForm,
                                       VenueFormManager)
from resource_hub.venues.models import Venue
from resource_hub.venues.tables import VenuesTable

TTL = 60 * 5


# @cache_page(TTL)
def index(request):
    return render(request, 'venues/index.html')

# Admin section
@method_decorator(login_required, name='dispatch')
class VenuesManage(View):
    def get(self, request):
        user = request.user
        query = Q(owner=user.pk)
        sub_condition = Q(owner__organization__members=user)
        sub_condition.add(
            Q(owner__organization__organizationmember__role__gte=OrganizationMember.ADMIN), Q.AND)
        query.add(sub_condition, Q.OR)
        venues = Venue.objects.filter(query)

        if venues:
            data = []
            for r in venues:
                data.append({
                    'name': r.name,
                    'venue_id': r.id,
                    'owner': r.owner,
                })
            venues_table = VenuesTable(data)
        else:
            venues_table = None

        context = {
            'venues_table': venues_table,
        }
        return render(request, 'venues/control/venues_manage.html', context)


@method_decorator(login_required, name='dispatch')
class VenuesCreate(View):
    def get(self, request):
        venue_form = VenueFormManager(request.user)

        return render(request, 'venues/control/venues_create.html', venue_form.get_forms())

    def post(self, request):
        venue_form = VenueFormManager(request.user, request)

        if venue_form.is_valid():
            venue_form.save(request.actor)

            message = ('The venue has been created')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:venues_manage'))

        return render(request, 'venues/control/venues_create.html', venue_form.get_forms())


@method_decorator(login_required, name='dispatch')
class VenuesProfileEdit(View):
    template_name = 'venues/control/venues_profile_edit.html'

    def get(self, request, venue_id):
        venue = get_object_or_404(Venue, pk=venue_id)
        venue_form = VenueFormManager(request.user, instance=venue)
        return render(request, self.template_name, venue_form.get_forms())

    def post(self, request, venue_id):
        venue = get_object_or_404(Venue, pk=venue_id)
        venue_form = VenueFormManager(
            request.user,
            request,
            instance=venue,
        )

        if venue_form.is_valid():
            venue_form.save(venue.owner)
            message = _('The venue has been updated')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:venues_profile_edit', kwargs={'venue_id': venue_id}))

        return render(request, self.template_name, venue_form.get_forms())


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
        return render(request, self.template_name, VenueContractFormManager(venue).get_forms())

    def post(self, request, location_slug, venue_slug):
        venue = get_object_or_404(
            Venue, slug=venue_slug, location__slug=location_slug)
        venue_contract_form = VenueContractFormManager(venue, request)
        if venue_contract_form.is_valid():
            venue_contract = venue_contract_form.save()
            message = _(
                'The event has been created successfully. You can review it and either confirm or cancel.')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_contracts_manage_details', kwargs={'pk': venue_contract.pk}))
        return render(request, self.template_name, venue_contract_form.get_forms())


@method_decorator(login_required, name='dispatch')
class EventsManageDetails(View):
    def get(self, request, event):
        return
