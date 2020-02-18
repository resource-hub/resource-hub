from django import forms
from django.utils.translation import ugettext_lazy as _

from core.widgets import TimeInputCustom
from django_summernote.widgets import SummernoteWidget
from venues.models import Event, Venue, VenueContractProcedure


class VenueForm(forms.ModelForm):
    description = forms.CharField(widget=SummernoteWidget())

    class Meta:
        model = Venue
        fields = ['name', 'description', 'location',
                  'thumbnail_original', 'bookable']


# class VenueProcedureForm(forms.ModelForm):
#     terms_and_conditions = forms.CharField(widget=SummernoteWidget())

#     class Meta:
#         model = VenueContractProcedure
#         fields = ['terms_and_conditions', 'notes',
#                   'payment_methods', 'tax_rate', 'trigger', ]


class VenueFormManager():
    def __init__(self, request=None):
        if request is None:
            self.room_form = VenueForm()
            self.venue_procedure = VenueProcedureForm()
        else:
            self.room_form = VenueForm(request.POST, request.FILES)
            self.venue_procedure = VenueProcedureForm(request.POST)

    def is_valid(self):
        return self.room_form.is_valid() and self.venue_procedure.is_valid()

    def get_forms(self):
        return {
            'room_form': self.room_form,
            'venue_procedure': self.venue_procedure,
        }

    def save(self, owner, commit=True):
        new_room = self.room_form.save(commit=False)
        new_room.owner = owner
        self.venue_procedure.save(commit=commit)

        if commit:
            new_room.save()


class EventForm(forms.ModelForm):
    description = forms.CharField(widget=SummernoteWidget())
    thumbnail_original = forms.ImageField(required=True)
    is_public = forms.BooleanField(
        required=False,
        label=_('Make the event publically visible?'),
    )
    start = forms.TimeField(widget=TimeInputCustom())
    end = forms.TimeField(widget=TimeInputCustom())

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
