from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse

from rooms.forms import RoomForm
from rooms.models import Room
from rooms.tables import RoomsTable


def index(request):
    return render(request, 'rooms/index.html')


@method_decorator(login_required, name='dispatch')
class Manage(View):
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
        return render(request, 'admin/rooms_manage.html', context)


@method_decorator(login_required, name='dispatch')
class Create(View):
    def get(self, request):
        room_form = RoomForm()
        context = {
            'room_form': room_form,
        }
        return render(request, 'admin/rooms_create.html', context)

    def post(self, request):
        room_form = RoomForm(request.POST)

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
        return render(request, 'admin/room_create.html', context)
