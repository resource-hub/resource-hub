from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.forms import model_to_dict
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.decorators.cache import cache_page

from core.models import OrganizationMember
from rooms.forms import RoomForm, EventForm
from rooms.models import Room
from rooms.tables import RoomsTable

TTL = 60 * 5


# @cache_page(TTL)
def index(request):
    return render(request, 'rooms/index.html')

# Admin section
@method_decorator(login_required, name='dispatch')
class RoomsManage(View):
    def get(self, request):
        user = request.user
        query = Q(owner=user.pk)
        sub_condition = Q(owner__organization__members=user)
        sub_condition.add(
            Q(owner__organization__organizationmember__role__gte=OrganizationMember.ADMIN), Q.AND)
        query.add(sub_condition, Q.OR)
        rooms = Room.objects.filter(query)

        if rooms:
            data = []
            for r in rooms:
                data.append({
                    'name': r.name,
                    'room_id': r.id,
                    'owner': r.owner,
                })
            rooms_table = RoomsTable(data)
        else:
            rooms_table = None

        context = {
            'rooms_table': rooms_table,
        }
        return render(request, 'rooms/admin/rooms_manage.html', context)


@method_decorator(login_required, name='dispatch')
class RoomsCreate(View):
    def get(self, request):
        room_form = RoomForm()
        context = {
            'room_form': room_form,
        }
        return render(request, 'rooms/admin/rooms_create.html', context)

    def post(self, request):
        room_form = RoomForm(request.POST, request.FILES)

        if room_form.is_valid():
            new_room = room_form.save(commit=False)
            new_room.owner = request.actor
            new_room.save()

            message = ('The room has been created')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('admin:rooms_manage'))

        context = {
            'room_form': room_form,
        }
        return render(request, 'rooms/admin/rooms_create.html', context)


class RoomsProfileEdit(View):
    template_name = 'rooms/admin/rooms_profile_edit.html'

    def get(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        room_form = RoomForm(initial=model_to_dict(room))
        context = {
            'room_form': room_form
        }
        return render(request, self.template_name, context)

    def post(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        room_form = RoomForm(
            request.POST, request.FILES, instance=room)

        if room_form.is_valid():
            room_form.save()
            return redirect(reverse('admin:rooms_profile_edit', kwargs={'room_id': room_id}))

        context = {
            'room_form': room_form,
        }

        return render(request, self.template_name, context)


class RoomDetails(View):
    def get(self, request, room_id):
        room = get_object_or_404(Room, pk=room_id)
        context = {'room': room}
        return render(request, 'rooms/room_details.html', context)


class RoomEventsCreate(View):
    template_name = 'rooms/room_events_create.html'

    def get(self, request, room_id):
        context = {'event_form': EventForm(room_id)}
        return render(request, self.template_name, context)

    def post(self, request, room_id):
        event_form = EventForm(room_id, request.POST, request.FILES)
        if event_form.is_valid():
            event_form.save(request.actor, request.user)
            message = _('The event has been created successfully')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('rooms:room_details', kwargs={'room_id': room_id}))
        else:
            context = {'event_form': event_form}
            return render(request, self.template_name, context)
