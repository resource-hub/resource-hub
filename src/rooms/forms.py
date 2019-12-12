from django import forms
from rooms.models import Room, Event


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ['created_at', 'owner', 'gallery']


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['created_at', 'created_by',
                   'updated_at', 'updated_by', ]
