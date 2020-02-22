from django import forms
from django.utils.translation import ugettext_lazy as _

from django_summernote.widgets import SummernoteWidget
from resource_hub.core.models import Location, PaymentMethod
from resource_hub.core.utils import get_associated_objects
from resource_hub.core.widgets import TimeInputCustom
from resource_hub.venues.models import Event, Venue, VenueContractProcedure


class VenueForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(VenueForm, self).__init__(*args, **kwargs)
        self.fields['location'].queryset = get_associated_objects(
            user,
            Location
        )
    description = forms.CharField(widget=SummernoteWidget())

    class Meta:
        model = Venue
        fields = ['name', 'description', 'location',
                  'thumbnail_original', 'bookable']


class VenueProcedureForm(forms.ModelForm):
    def __init__(self, user, *args, **kwargs):
        super(VenueProcedureForm, self).__init__(*args, **kwargs)
        self.fields['payment_methods'].queryset = get_associated_objects(
            user,
            PaymentMethod
        ).select_subclasses()

    terms_and_conditions = forms.CharField(widget=SummernoteWidget())

    class Meta:
        model = VenueContractProcedure
        fields = ['terms_and_conditions', 'notes',
                  'payment_methods', 'tax_rate', 'trigger', ]
        help_texts = {
            'payment_methods': _('Choose the payment methods you want to use for this venue')
        }


class VenueFormManager():
    def __init__(self, user, request=None):
        if request is None:
            self.venue_form = VenueForm(user)
            self.venue_procedure = VenueProcedureForm(user)
        else:
            self.venue_form = VenueForm(user, request.POST, request.FILES)
            self.venue_procedure = VenueProcedureForm(
                user, data=request.POST)

    def is_valid(self):
        return self.venue_form.is_valid() and self.venue_procedure.is_valid()

    def get_forms(self):
        return {
            'venue_form': self.venue_form,
            'venue_procedure': self.venue_procedure,
        }

    def save(self, owner, commit=True):
        new_venue = self.venue_form.save(commit=False)
        new_venue.owner = owner
        self.venue_procedure.save(commit=commit)

        if commit:
            new_venue.save()


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

    def __init__(self, venue_id, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.venue_id = venue_id

    def save(self, organizer, user, commit=True):
        new_event = super(EventForm, self).save(commit=False)
        new_event.organizer = organizer
        new_event.created_by = user
        new_event.updated_by = user
        new_event.venue_id = self.venue_id

        if commit:
            new_event.save()
        return new_event
