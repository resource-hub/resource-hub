from django import forms
from django.contrib.admin.widgets import AdminDateWidget
from django.db.models import Q
from django.forms import inlineformset_factory
from django.utils.translation import ugettext_lazy as _

from datetimepicker.widgets import DateTimePicker
from django_summernote.widgets import SummernoteWidget
from resource_hub.core.fields import HTMLField
from resource_hub.core.forms import (ContractProcedureForm, FormManager,
                                     PriceProfileFormSet)
from resource_hub.core.models import (ContractTrigger, Location, PaymentMethod,
                                      PriceProfile)
from resource_hub.core.utils import get_associated_objects
from resource_hub.core.widgets import TimeInputCustom

from .models import Event, Venue, VenueContract, VenueContractProcedure


class VenueForm(forms.ModelForm):
    def __init__(self, request, *args, **kwargs):
        user = request.user
        super(VenueForm, self).__init__(*args, **kwargs)
        self.fields['location'].queryset = get_associated_objects(
            user,
            Location
        )
    description = HTMLField()

    class Meta:
        model = Venue
        fields = ['name', 'description', 'location',
                  'thumbnail_original', 'bookable', 'price', 'equipment', 'contract_procedure', ]
        help_texts = {
            'bookable': _('Do you want to use the platform\'s booking logic?'),
        }


class VenueContractProcedureForm(ContractProcedureForm):
    def __init__(self, *args, **kwargs):
        super(VenueContractProcedureForm, self).__init__(*args, **kwargs)
        # self.fields['venues'].queryset = get_associated_objects(
        #     self.request.user,
        #     Venue
        # )

    class Meta(ContractProcedureForm.Meta):
        model = VenueContractProcedure
        # fields = ['venues', ] + ContractProcedureForm.Meta.fields
        new = {
            'venues': _('Select the venues that you want to make bookable. A venue can only be associated with one procedure. Existing connections will be overwritten.'),
        }
        help_texts = {
            **ContractProcedureForm.Meta.help_texts,
            **new
        }

    def save(self, commit=True, **kwargs):
        new_venue_contract_procedure = super(
            VenueContractProcedureForm, self).save(commit=False, **kwargs)
        new_venue_contract_procedure.owner = self.request.actor

        if commit:
            new_venue_contract_procedure.save()
            self.save_m2m()
            for venue in new_venue_contract_procedure.venues.all():
                venue.contract_procedure = new_venue_contract_procedure
        return new_venue_contract_procedure


class VenueContractProcedureFormManager(FormManager):

    def __init__(self, request, instance=None):
        if not request.POST:
            self.forms = {
                'contract_procedure_form': VenueContractProcedureForm(request, instance=instance),
                'price_profile_form_set': PriceProfileFormSet(instance=instance)
            }
        else:
            self.forms = {
                'contract_procedure_form': VenueContractProcedureForm(request, data=request.POST, files=request.FILES, instance=instance),
                'price_profile_form_set': PriceProfileFormSet(data=request.POST, files=request.FILES, instance=instance)
            }

    def save(self):
        new_venue_contract_procedure = self.forms['contract_procedure_form'].save(
        )
        for form in self.forms['price_profile_form_set'].save(commit=False):
            form.contract_procedure = new_venue_contract_procedure
            form.save()

        # for venue in new_venue_contract_procedure.venues.all():
        #     venue.contract_procedure = new_venue_contract_procedure
        #     venue.save()

        return new_venue_contract_procedure

        # class VenueFormManager():
        #     def __init__(self, user, request=None, instance=None):
        #         self.request = request
        #         venue = instance if instance else None
        #         venue_procedure = instance.contract_procedure if instance else None

        #         if request is None:
        #             self.venue_form = VenueForm(user, instance=venue)
        #             self.venue_procedure = VenueContractProcedureForm(
        #                 user, instance=venue_procedure)
        #         else:
        #             self.venue_form = VenueForm(
        #                 user, request.POST,
        #                 request.FILES,
        #                 instance=venue,
        #             )
        #             self.venue_procedure = VenueContractProcedureForm(
        #                 user,
        #                 data=request.POST,
        #                 instance=venue_procedure,
        #             )

        #     def is_valid(self):
        #         if self.request.POST.get('bookable', False):
        #             return self.venue_form.is_valid() and self.venue_procedure.is_valid()
        #         return self.venue_form.is_valid()

        #     def get_forms(self):
        #         return {
        #             'venue_form': self.venue_form,
        #             'venue_procedure': self.venue_procedure,
        #         }

        #     def save(self, owner, commit=True):
        #         new_venue = self.venue_form.save(commit=False)
        #         new_venue.owner = owner
        #         if self.venue_form.cleaned_data['bookable']:
        #             new_venue_procedure = self.venue_procedure.save(commit=True)
        #             new_venue.contract_procedure = new_venue_procedure

        #         if commit:
        #             new_venue.save()
        #         return new_venue


class EventForm(forms.ModelForm):
    description = forms.CharField(widget=SummernoteWidget())
    thumbnail_original = forms.ImageField(required=True)
    is_public = forms.BooleanField(
        initial=True,
        help_text=_(
            'List the event in public feeds and show its content to third parties?'),
    )
    dtstart = forms.DateTimeField(
        label=_('Start of the event'),
    )
    dtend = forms.DateTimeField(
        label=_('End of the event'),
    )

    def __init__(self, venue, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.venue = venue
        self.new_event = None
        self.dtlast = None
        self.occurrences = []

    class Meta:
        model = Event
        fields = ['name', 'description', 'dtstart', 'dtend', 'recurrences', 'thumbnail_original',
                  'tags', 'category', 'is_public', ]
        labels = {
            'recurrences': _('Recurs on')
        }

    def get_occurrences(self):
        return self.occurrences

    def clean_dtend(self):
        dtstart = self.cleaned_data['dtstart']
        dtend = self.cleaned_data['dtend']

        if dtstart > dtend:
            raise forms.ValidationError(
                _('Start of event is after end of event'), code='start-after-end')

        if dtstart == dtend:
            raise forms.ValidationError(
                _('Start of event is equal to end'), code='start-equal-to-end')
        return dtend

    def clean_recurrences(self):
        '''
        quick, dirty and naive conflict detection (polynomial runtime)
        work in progress
        '''

        recurrences = self.cleaned_data['recurrences']
        dtstart = self.cleaned_data['dtstart'].replace(tzinfo=None)
        dtend = self.cleaned_data['dtend'].replace(tzinfo=None)
        recurrences.dtstart = dtstart
        dates = recurrences.occurrences()
        for date in dates:
            # get last occurrence and apply times to dates

            t = dtstart.time()
            occurrence_start = date.replace(
                hour=t.hour, minute=t.minute, second=t.second)
            t = dtend.time()
            occurrence_end = date.replace(
                hour=t.hour, minute=t.minute, second=t.second)
            self.occurrences.append(
                (occurrence_start, occurrence_end)
            )
            self.dtlast = occurrence_end

        # query existing events in planned timeframe
        start_inside = Q(
            dtstart__lte=dtstart,
        )
        start_inside.add(
            Q(dtlast__gte=dtstart),
            Q.AND
        )
        last_inside = Q(
            dtstart__lte=self.dtlast,
        )
        last_inside.add(
            Q(dtlast__gte=self.dtlast),
            Q.AND
        )
        intersect = start_inside
        intersect.add(last_inside, Q.OR)

        query = Q(venue=self.venue)
        query.add(Q(intersect), Q.AND)

        current_events = Event.objects.filter(
            query
        )

        # iterate for conflicts (O(n^3) worst case ha!)
        conflicts = []
        for occurrence in self.occurrences:
            new_date_start = occurrence[0]
            new_date_end = occurrence[1]
            for event in current_events:
                old_dates = event.recurrences.between(
                    dtstart,
                    self.dtlast,
                    dtstart=dtstart,
                    inc=True
                )

                for old_date in old_dates:
                    t = event.dtstart.time()
                    old_date_start = old_date.replace(
                        hour=t.hour, minute=t.minute, second=t.second, tzinfo=None)
                    t = event.dtlast.time()
                    old_date_end = old_date.replace(
                        hour=t.hour, minute=t.minute, second=t.second, tzinfo=None)
                    print("{} - {} | {} - {}".format(new_date_start,
                                                     new_date_end, old_date_start, old_date_end))
                    if (
                        (
                            old_date_start <= new_date_start and
                            old_date_end >= new_date_start
                        ) or
                        (
                            old_date_start <= new_date_end and
                            old_date_start >= new_date_start
                        )
                    ):
                        conflicts.append(
                            _('There is a conflict with {} on {} to {}'.format(
                                event.name, new_date_start, new_date_end))
                        )
        if conflicts:
            raise forms.ValidationError(
                conflicts
            )

        return recurrences

    def pre_save(self, *args, **kwargs):
        # print(self.new_event.recurrences.count())
        return False

    def save(self, request, *args, commit=True, **kwargs):
        self.new_event = super(EventForm, self).save(
            commit=False, *args, **kwargs)
        self.new_event.organizer = request.actor
        self.new_event.created_by = request.user
        self.new_event.updated_by = request.user
        self.new_event.venue = self.venue
        self.new_event.recurrences.dtstart = self.new_event.dtstart.replace(
            tzinfo=None)
        if self.dtlast is None:
            self.new_event.dtlast = self.new_event.dtend
        else:
            self.new_event.dtlast = self.dtlast

        self.new_event.save()
        self.save_m2m()
        return self.new_event


class VenueContractForm(forms.ModelForm):
    def __init__(self, venue, request, *args, **kwargs):
        super(VenueContractForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['payment_method'].queryset = venue.contract_procedure.payment_methods.select_subclasses()
        query = Q(addressee__isnull=True)
        query.add(
            Q(addressee=self.request.actor),
            Q.OR
        )
        self.fields['price_profile'].queryset = PriceProfile.objects.filter(
            query
        ).order_by('-discount')
        self.initial['price_profile'] = self.fields['price_profile'].queryset[0]
        self.fields['venues'].queryset = Venue.objects.filter(
            contract_procedure=venue.contract_procedure
        )

    class Meta:
        model = VenueContract
        fields = ['price_profile', 'payment_method', 'venues', ]
        help_texts = {
            'price_profile': _('Available discounts granted to certain groups and entities')
        }


class VenueContractFormManager():
    def __init__(self, venue, request):
        self.request = request
        self.venue = venue
        self.venue_contract_form = VenueContractForm(
            self.venue,
            self.request,
            request.POST
        ) if request.POST else VenueContractForm(self.venue, self.request)
        self.event_form = EventForm(
            self.venue,
            request.POST,
            request.FILES
        ) if request.POST else EventForm(self.venue)

    @property
    def occurrences(self):
        return self.event_form.get_occurrences()

    def get_forms(self):
        return {
            'venue_contract_form': self.venue_contract_form,
            'event_form': self.event_form,
        }

    def is_valid(self):
        return (
            self.venue_contract_form.is_valid() and
            self.event_form.is_valid()
        )

    def save(self, commit=True):
        user = self.request.user
        actor = self.request.actor
        new_venue_contract = self.venue_contract_form.save(commit=False)
        new_venue_contract.state = VenueContract.STATE.PENDING
        new_venue_contract.creditor = self.venue.owner
        new_venue_contract.debitor = actor
        new_venue_contract.created_by = user
        new_venue_contract.contract_procedure = self.venue.contract_procedure
        new_event = self.event_form.save(self.request, commit=True)
        new_venue_contract.event = new_event

        if commit:
            new_venue_contract.save()
            self.venue_contract_form.save_m2m()
        return new_venue_contract
