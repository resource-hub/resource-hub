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

from core.models import OrganizationMember
from venues.forms import EventForm, VenueForm, VenueFormManager
from venues.models import Venue
from venues.tables import VenuesTable

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
                    'room_id': r.id,
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
        venue_form = VenueFormManager()

        return render(request, 'venues/control/venues_create.html', venue_form.get_forms())

    def post(self, request):
        venue_form = VenueFormManager(request)

        if venue_form.is_valid():
            venue_form.save(request.actor)

            message = ('The room has been created')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:venues_manage'))

        return render(request, 'venues/control/venues_create.html', venue_form.get_forms())


class VenuesProfileEdit(View):
    template_name = 'venues/control/venues_profile_edit.html'

    def get(self, request, room_id):
        room = get_object_or_404(Venue, pk=room_id)
        room_form = VenueForm(initial=model_to_dict(room))
        context = {
            'room_form': room_form
        }
        return render(request, self.template_name, context)

    def post(self, request, room_id):
        room = get_object_or_404(Venue, pk=room_id)
        room_form = VenueForm(
            request.POST, request.FILES, instance=room)

        if room_form.is_valid():
            room_form.save()
            return redirect(reverse('control:venues_profile_edit', kwargs={'room_id': room_id}))

        context = {
            'room_form': room_form,
        }

        return render(request, self.template_name, context)


class VenueDetails(View):
    def get(self, request, room_id):
        room = get_object_or_404(Venue, pk=room_id)
        context = {'room': room}
        return render(request, 'venues/room_details.html', context)


class VenueEventsCreate(View):
    template_name = 'venues/room_events_create.html'

    def get(self, request, room_id):
        context = {'event_form': EventForm(room_id), }
        return render(request, self.template_name, context)

    def post(self, request, room_id):
        event_form = EventForm(room_id, request.POST, request.FILES)
        if event_form.is_valid():
            event_form.save(request.actor, request.user)
            message = _('The event has been created successfully')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('venues:room_details', kwargs={'room_id': room_id}))
        else:
            context = {'event_form': event_form}
            return render(request, self.template_name, context)
