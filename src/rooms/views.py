from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.decorators.cache import cache_page

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
        rooms = Room.objects.all().filter(owner__pk=request.actor.id)

        if rooms:
            data = []
            for o in rooms:
                data.append({
                    'name': o.name,
                    'id': o.id,
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
            return redirect(reverse('rooms:manage'))

        context = {
            'room_form': room_form,
        }
        return render(request, 'rooms/admin/rooms_create.html', context)


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
            print(event_form.cleaned_data['recurrences'])
            event_form.save(request.actor, request.user)
            message = _('The event has been created successfully')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('rooms:room_details', kwargs={'room_id': room_id}))
        else:
            context = {'event_form': event_form}
            return render(request, self.template_name, context)
