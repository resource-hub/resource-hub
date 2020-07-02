from datetime import datetime
from decimal import Decimal

from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.utils.timezone import get_current_timezone
from django.utils.translation import gettext_lazy as _

from resource_hub.core.fields import HTMLField
from resource_hub.core.forms import (BaseForm, ContractProcedureForm,
                                     FormManager, GalleryImageFormSet,
                                     PriceForm, PriceProfileFormSet)
from resource_hub.core.models import Gallery, Location, PriceProfile
from resource_hub.core.utils import get_authorized_actors, timespan_conflict

from .models import (Equipment, EquipmentPrice, Event, Venue, VenueContract,
                     VenueContractProcedure, VenuePrice)


class VenueForm(BaseForm):
    def __init__(self, user, actor, data=None, files=None, instance=None, **kwargs):
        super(VenueForm, self).__init__(
            user, actor, data=data, files=files, instance=instance, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(
            Q(owner=self.actor) | Q(is_editable=True)
        )
        self.fields['contract_procedure'].queryset = VenueContractProcedure.objects.filter(
            owner=self.actor)

        self._update_attrs({
            'contract_procedure': {'class': 'booking-item required'},
        })

    description = HTMLField()

    class Meta:
        model = Venue
        fields = ['name', 'description', 'location',
                  'thumbnail_original', 'owner', 'bookable', 'contract_procedure', ]
        help_texts = {
            'bookable': _('Do you want to use the platform\'s booking logic?'),
        }

    def _update_attrs(self, fields):
        for field, val in fields.items():
            self.fields[field].widget.attrs.update(val)


class VenueFormManager(FormManager):
    def __init__(self, user, actor, *args, data=None, files=None, instance=None, **kwargs):
        gallery_instance = instance.gallery if instance else None
        if data:
            bookable = data.get('bookable', False)
            price_formset = VenuePriceFormset(
                data=data,
                instance=instance,
            ) if bookable else forms.Form()
            if not bookable:
                price_formset.is_bound = True
            self.forms = {
                'venue_form': VenueForm(
                    user,
                    actor,
                    data=data,
                    files=files,
                    instance=instance,
                ),
                'gallery_formset': GalleryImageFormSet(
                    data=data,
                    files=files,
                    instance=gallery_instance,
                ),
                'price_formset': price_formset,
                'equipment_formset': EquipmentFormset(
                    data=data,
                    files=files,
                    instance=instance
                ),
            }
        else:
            self.forms = {
                'venue_form': VenueForm(
                    user,
                    actor,
                    instance=instance,
                ),
                'gallery_formset': GalleryImageFormSet(
                    instance=gallery_instance,
                ),
                'price_formset': VenuePriceFormset(
                    instance=instance,
                ),
                'equipment_formset': EquipmentFormset(instance=instance),
            }

    def save(self):
        new_venue = self.forms['venue_form'].save()
        first = True
        if new_venue.gallery is None:
            new_venue.gallery = Gallery.objects.create()

        self.forms['gallery_formset'].instance = new_venue.gallery
        self.forms['gallery_formset'].save()
        if new_venue.bookable:
            self.forms['price_formset'].instance = new_venue
            for price in self.forms['price_formset'].save(commit=False):
                if first:
                    new_venue.price = price
                    first = False
            self.forms['price_formset'].save()
            self.forms['equipment_formset'].instance = new_venue
            self.forms['equipment_formset'].save()
        new_venue.save()
        return new_venue


class VenueContractProcedureForm(ContractProcedureForm):
    class Meta(ContractProcedureForm.Meta):
        model = VenueContractProcedure

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
        if request.POST:
            self.forms = {
                'contract_procedure_form': VenueContractProcedureForm(request, data=request.POST, files=request.FILES, instance=instance),
                'price_profile_form_set': PriceProfileFormSet(data=request.POST, files=request.FILES, instance=instance)
            }
        else:
            self.forms = {
                'contract_procedure_form': VenueContractProcedureForm(request, instance=instance),
                'price_profile_form_set': PriceProfileFormSet(instance=instance)
            }

    def save(self):
        new_venue_contract_procedure = self.forms['contract_procedure_form'].save(
        )
        for form in self.forms['price_profile_form_set'].save(commit=False):
            form.contract_procedure = new_venue_contract_procedure
            form.save()

        for deleted_form in self.forms['price_profile_form_set'].deleted_objects:
            deleted_form.delete()

        return new_venue_contract_procedure


class EventForm(forms.ModelForm):
    description = HTMLField()
    dtstart = forms.DateTimeField(
        label=_('Start of the event'),
    )
    dtend = forms.DateTimeField(
        label=_('End of the event'),
    )

    def __init__(self, venue, request, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.request = request
        self.new_event = None
        self.dtlast = None
        self.occurrences = []
        self.fields['venues'].queryset = Venue.objects.filter(
            contract_procedure=venue.contract_procedure
        )
        self.initial['venues'] = venue

    class Meta:
        model = Event
        fields = ['venues', 'name', 'description', 'dtstart', 'dtend', 'recurrences', 'thumbnail_original',
                  'category', 'is_public', ]
        labels = {
            'recurrences': _('Recurs on'),
            'name': _('Event name'),
        }
        help_texts = {
            'venues': _('If available you can book several venues at once'),
            'is_public': _('List the event in public feeds and show its content to third parties?'),
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

    def _find_conflicts(self, venue, dtstart, dtlast, occurrences):
        # query existing events in planned timeframe
        query = Q(dtlast__gt=dtstart)
        query.add(
            Q(dtstart__lt=dtlast),
            Q.AND
        )
        query.add(Q(venues=venue), Q.AND)

        current_events = Event.objects.filter(
            query
        )
        conflicts = []
        # iterate for conflicts (O(n^3) worst case ha!)
        for occurrence in occurrences:
            new_date_start = occurrence[0]
            new_date_end = occurrence[1]
            for event in current_events:
                old_dates = event.recurrences.between(
                    dtstart.replace(hour=0, minute=0, second=0),
                    dtlast,
                    dtstart=event.dtstart,
                    inc=True
                )

                for old_date in old_dates:
                    old_date_start = datetime.combine(
                        old_date.date(), event.dtstart.time(), event.dtstart.tzinfo)
                    old_date_end = datetime.combine(
                        old_date.date(), event.dtend.time(), event.dtend.tzinfo)
                    # print("{} - {} | {} - {}".format(new_date_start,
                    #                                  new_date_end, old_date_start, old_date_end))
                    if (
                        timespan_conflict(
                            new_date_start, new_date_end, old_date_start, old_date_end)
                    ):
                        client_tz = get_current_timezone()
                        old_date_start = old_date_start.astimezone(client_tz)
                        old_date_end = old_date_end.astimezone(client_tz)
                        conflicts.append(
                            _('There is a conflict with {}@{} at {} to {}'.format(
                                event.name, venue.name, old_date_start.strftime('%c'), old_date_end.strftime('%c')))
                        )
        return conflicts

    def clean_recurrences(self):
        '''
        quick, dirty and naive conflict detection (polynomial runtime)
        work in progress
        '''

        recurrences = self.cleaned_data.get('recurrences')
        for rrule in recurrences.rrules:
            if rrule.count or rrule.until:
                continue
            raise forms.ValidationError(
                _('The recurrence has to be limited'), code='infinite-recurrence')

        dtstart = self.cleaned_data.get('dtstart')
        dtend = self.cleaned_data.get('dtend')
        recurrences.dtstart = dtstart
        dates = recurrences.occurrences()
        if not self.errors:
            for date in dates:
                # get last occurrence and apply times to dates

                occurrence_start = datetime.combine(
                    date.date(), dtstart.time(), dtstart.tzinfo)
                occurrence_end = datetime.combine(
                    date.date(), dtend.time(), dtend.tzinfo)
                self.occurrences.append(
                    (occurrence_start, occurrence_end)
                )
                self.dtlast = occurrence_end

            conflicts = []
            for venue in self.cleaned_data['venues']:
                conflicts = conflicts + self._find_conflicts(
                    venue, dtstart, self.dtlast, self.occurrences)

            if conflicts:
                raise forms.ValidationError(
                    conflicts
                )

            return recurrences

    def save(self, *args, commit=True, **kwargs):
        self.new_event = super(EventForm, self).save(
            commit=False, *args, **kwargs)
        self.new_event.organizer = self.request.actor
        self.new_event.created_by = self.request.user
        self.new_event.updated_by = self.request.user
        self.new_event.recurrences.dtstart = self.new_event.dtstart
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
        self.venue = venue
        self.fields['payment_method'].queryset = venue.contract_procedure.payment_methods.select_subclasses(
        ).order_by('fee_absolute_value')

        # discounts for actors
        query = Q(addressee__isnull=True)
        query.add(
            Q(addressee=self.request.actor),
            Q.OR
        )
        query.add(
            Q(addressee__organization__organizationmember__user=self.request.user),
            Q.OR
        )
        price_profiles = PriceProfile.objects.filter(
            query
        ).distinct()
        self.fields['price_profile'].queryset = price_profiles.order_by(
            '-discount')
        if self.fields['price_profile'].queryset:
            self.initial['price_profile'] = self.fields['price_profile'].queryset[0]
            self.initial['payment_method'] = self.fields['payment_method'].queryset[0]

    def clean(self):
        data = super(VenueContractForm, self).clean()
        address = self.request.actor.address
        print(self.cleaned_data['price_profile'].discount)
        print(self.cleaned_data['price_profile']
              and self.cleaned_data['price_profile'].discount != Decimal('100'))
        if (address.street is None or address.street_number is None or address.postal_code is None or address.city is None) and (
            self.venue.price.value != Decimal(
                '0') and (self.cleaned_data['price_profile'] and self.cleaned_data['price_profile'].discount != Decimal('100'))
        ):
            raise forms.ValidationError(
                _('to create bookings you need to set your billing address'), code='address-not-set')

    class Meta:
        model = VenueContract
        fields = ['price_profile', 'payment_method', ]
        help_texts = {
            'price_profile': _('Available discounts granted to certain groups and entities. The discounts will be applied to the base prices below.')
        }


class VenueContractFormManager():
    def __init__(self, venue, request):
        self.request = request
        self.venue = venue

        self.venue_contract_form = VenueContractForm(
            self.venue,
            self.request,
            data=self.request.POST
        ) if request.POST else VenueContractForm(self.venue, self.request)
        self.event_form = EventForm(
            self.venue,
            self.request,
            data=self.request.POST,
            files=self.request.FILES
        ) if self.request.POST else EventForm(self.venue, self.request)

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
        new_venue_contract.creditor = self.venue.owner
        new_venue_contract.debitor = actor
        new_venue_contract.created_by = user
        new_venue_contract.contract_procedure = self.venue.contract_procedure
        new_venue_contract.terms_and_conditions = self.venue.contract_procedure.terms_and_conditions
        new_event = self.event_form.save()
        new_venue_contract.event = new_event

        if commit:
            new_venue_contract.save()
            self.venue_contract_form.save_m2m()
        return new_venue_contract


VenuePriceFormset = inlineformset_factory(
    Venue,
    VenuePrice,
    form=PriceForm,
    extra=0,
    min_num=1,
    can_order=True,
)


class EquipmentForm(forms.ModelForm):
    class Meta:
        model = Equipment
        fields = ['name', 'quantity',
                  'thumbnail_original', ]


EquipmentPriceFormset = inlineformset_factory(
    Equipment,
    EquipmentPrice,
    form=PriceForm,
    extra=0,
    min_num=1,
    can_order=True,
)


class BaseEquipmentFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseEquipmentFormset, self).__init__(*args, **kwargs)
        self.nested_empty_form = None
        self.nested_empty_management_form = None

    def add_fields(self, form, index):
        super(BaseEquipmentFormset, self).add_fields(form, index)

        # save the formset in the 'nested' property
        form.nested = EquipmentPriceFormset(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='equipment-price-%s-%s' % (
                form.prefix,
                EquipmentPriceFormset.get_default_prefix()),
        )

        self.nested_empty_form = form.nested.empty_form
        self.nested_empty_management_form = form.nested.management_form

    def is_valid(self):
        result = super(BaseEquipmentFormset, self).is_valid()

        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
        return result

    def save(self, commit=True):
        result = super(BaseEquipmentFormset, self).save(commit=commit)
        for form in self.forms:
            if hasattr(form, 'nested'):
                if not self._should_delete_form(form):
                    form.nested.instance = form.instance
                    first = True
                    for nested_form in form.nested.save(commit=False):
                        if first:
                            first = False
                            form.instance.price = nested_form.price_ptr
                            form.instance.save()
                    if commit:
                        form.nested.save()
        return result


EquipmentFormset = inlineformset_factory(
    Venue,
    Equipment,
    formset=BaseEquipmentFormset,
    form=EquipmentForm,
    min_num=0,
    extra=0,
)
