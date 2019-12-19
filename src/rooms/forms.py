from django import forms
from django.utils.translation import ugettext_lazy as _

from django_summernote.widgets import SummernoteWidget

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
        label=_(
            'Make the event publically visible?'),
    )

    class Meta:
        model = Event
        fields = ['name', 'description', 'thumbnail_original',
                  'tags', 'category', 'is_public', 'recurrences']
