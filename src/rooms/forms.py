from django import forms

from django_summernote.widgets import SummernoteWidget

from rooms.models import Room, Event


class RoomForm(forms.ModelForm):
    description = forms.CharField(widget=SummernoteWidget())

    class Meta:
        model = Room
        exclude = ['created_at', 'owner', 'gallery']


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['created_at', 'created_by',
                   'updated_at', 'updated_by', ]
