from django import forms
from django.utils.translation import ugettext_lazy as _

from django_summernote.widgets import SummernoteWidget

from core.widgets import TimeInput
from rooms.models import Room, Event


class RoomForm(forms.ModelForm):
    description = forms.CharField(widget=SummernoteWidget())

    class Meta:
        model = Room
        exclude = ['created_at', 'owner', 'gallery']


class EventForm(forms.ModelForm):
    description = forms.CharField(widget=SummernoteWidget())
    thumbnail_original = forms.ImageField(required=True)
    is_public = forms.BooleanField(
        required=False,
        label=_('Make the event publically visible?'),
    )
    start = forms.TimeField(widget=TimeInput())
    end = forms.TimeField(widget=TimeInput())

    class Meta:
        model = Event
        fields = ['name', 'description', 'start', 'end', 'recurrences', 'thumbnail_original',
                  'tags', 'category', 'is_public', ]

    def __init__(self, room_id, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.room_id = room_id

    def save(self, organizer, user, commit=True):
        new_event = super(EventForm, self).save(commit=False)
        new_event.organizer = organizer
        new_event.created_by = user
        new_event.updated_by = user
        new_event.room_id = self.room_id

        if commit:
            new_event.save()
        return new_event
