from datetime import datetime
from decimal import Decimal

from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory
from django.forms.models import BaseInlineFormSet
from django.utils.timezone import get_current_timezone
from django.utils.translation import gettext_lazy as _
from resource_hub.core.fields import CustomMultipleChoiceField, HTMLField
from resource_hub.core.forms import (BaseForm, ContractProcedureForm,
                                     FormManager, GalleryImageFormSet,
                                     PriceForm, PriceProfileFormSet)
from resource_hub.core.models import Gallery, Location, PriceProfile
from resource_hub.core.utils import get_authorized_actors, timespan_conflict

from .models import (Workshop, WorkshopBooking, WorkshopContract,
                     WorkshopContractProcedure, WorkshopEquipment,
                     WorkshopEquipmentPrice, WorkshopPrice)


class WorkshopForm(BaseForm):
    def __init__(self, user, actor, data=None, files=None, instance=None, **kwargs):
        super(WorkshopForm, self).__init__(
            user, actor, data=data, files=files, instance=instance, **kwargs)
        self.fields['location'].queryset = Location.objects.filter(
            Q(owner=self.actor) | Q(is_editable=True)
        )
        self.fields['contract_procedure'].queryset = WorkshopContractProcedure.objects.filter(
            owner=self.actor)

        self._update_attrs({
            'contract_procedure': {'class': 'booking-item required'},
        })

    description = HTMLField()

    class Meta:
        model = Workshop
        fields = ['name', 'description', 'workplaces', 'location',
                  'thumbnail_original', 'owner', 'bookable', 'contract_procedure', ]
        help_texts = {
            'bookable': _('Do you want to use the platform\'s booking logic?'),
        }

    def _update_attrs(self, fields):
        for field, val in fields.items():
            self.fields[field].widget.attrs.update(val)


class WorkshopFormManager(FormManager):
    def __init__(self, user, actor, *args, data=None, files=None, instance=None, **kwargs):
        gallery_instance = instance.gallery if instance else None
        if data:
            bookable = data.get('bookable', False)
            price_formset = WorkshopPriceFormset(
                data=data,
                instance=instance,
            ) if bookable else forms.Form()
            if not bookable:
                price_formset.is_bound = True
            self.forms = {
                'workshop_form': WorkshopForm(
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
                'equipment_formset': WorkshopEquipmentFormset(
                    data=data,
                    files=files,
                    instance=instance
                ),
            }
        else:
            self.forms = {
                'workshop_form': WorkshopForm(
                    user,
                    actor,
                    instance=instance,
                ),
                'gallery_formset': GalleryImageFormSet(
                    instance=gallery_instance,
                ),
                'price_formset': WorkshopPriceFormset(
                    instance=instance,
                ),
                'equipment_formset': WorkshopEquipmentFormset(instance=instance),
            }

    def save(self):
        new_workshop = self.forms['workshop_form'].save()
        first = True
        if new_workshop.gallery is None:
            new_workshop.gallery = Gallery.objects.create()

        self.forms['gallery_formset'].instance = new_workshop.gallery
        self.forms['gallery_formset'].save()
        if new_workshop.bookable:
            self.forms['price_formset'].instance = new_workshop
            for price in self.forms['price_formset'].save(commit=False):
                if first:
                    new_workshop.base_price = price
                    first = False
            self.forms['equipment_formset'].instance = new_workshop
            self.forms['equipment_formset'].save()
            self.forms['price_formset'].save()
        new_workshop.save()
        return new_workshop


class WorkshopContractProcedureForm(ContractProcedureForm):
    class Meta(ContractProcedureForm.Meta):
        model = WorkshopContractProcedure

    def save(self, commit=True, **kwargs):
        new_workshop_contract_procedure = super(
            WorkshopContractProcedureForm, self).save(commit=False, **kwargs)
        new_workshop_contract_procedure.owner = self.request.actor

        if commit:
            new_workshop_contract_procedure.save()
            self.save_m2m()
            for workshop in new_workshop_contract_procedure.workshop_set.all():
                workshop.contract_procedure = new_workshop_contract_procedure
        return new_workshop_contract_procedure


class WorkshopContractProcedureFormManager(FormManager):
    def __init__(self, request, instance=None):
        if request.POST:
            self.forms = {
                'contract_procedure_form': WorkshopContractProcedureForm(request, data=request.POST, files=request.FILES, instance=instance),
                'price_profile_form_set': PriceProfileFormSet(data=request.POST, files=request.FILES, instance=instance)
            }
        else:
            self.forms = {
                'contract_procedure_form': WorkshopContractProcedureForm(request, instance=instance),
                'price_profile_form_set': PriceProfileFormSet(instance=instance)
            }

    def save(self):
        new_workshop_contract_procedure = self.forms['contract_procedure_form'].save(
        )
        for form in self.forms['price_profile_form_set'].save(commit=False):
            form.contract_procedure = new_workshop_contract_procedure
            form.save()

        for deleted_form in self.forms['price_profile_form_set'].deleted_objects:
            deleted_form.delete()

        return new_workshop_contract_procedure


class WorkshopBookingForm(forms.ModelForm):
    dtstart = forms.DateTimeField(
        label=_('Start of the booking'),
    )
    dtend = forms.DateTimeField(
        label=_('End of the booking'),
    )

    def __init__(self, workshop, request, *args, **kwargs):
        super(WorkshopBookingForm, self).__init__(*args, **kwargs)
        self.request = request
        self.new_booking = None
        self.dtlast = None
        self.occurrences = []
        self.fields['workshops'].queryset = Workshop.objects.filter(
            contract_procedure=workshop.contract_procedure
        )
        self.initial['workshops'] = [workshop, ]

    class Meta:
        model = WorkshopBooking
        fields = ['workshops', 'workplaces', 'dtstart', 'dtend', 'recurrences',
                  ]
        labels = {
            'recurrences': _('Recurs on'),
            'name': _('WorkshopBooking name'),
        }
        help_texts = {
            'workshops': _('If available you can book several workshops at once'),
            'is_public': _('List the booking in public feeds and show its content to third parties?'),
        }

    def get_occurrences(self):
        return self.occurrences

    def clean_dtend(self):
        dtstart = self.cleaned_data['dtstart']
        dtend = self.cleaned_data['dtend']

        if dtstart > dtend:
            raise forms.ValidationError(
                _('Start of booking is after end of booking'), code='start-after-end')

        if dtstart == dtend:
            raise forms.ValidationError(
                _('Start of booking is equal to end'), code='start-equal-to-end')
        return dtend

    def _find_conflicts(self, workshop, dtstart, dtlast, occurrences):
        # query existing bookings in planned timeframe
        query = Q(dtlast__gt=dtstart)
        query.add(
            Q(dtstart__lt=dtlast),
            Q.AND
        )
        query.add(Q(workshops=workshop), Q.AND)

        current_bookings = WorkshopBooking.objects.filter(
            query
        )
        conflicts = []
        # iterate for conflicts (O(n^3) worst case ha!)
        for occurrence in occurrences:
            new_date_start = occurrence[0]
            new_date_end = occurrence[1]
            for booking in current_bookings:
                old_dates = booking.recurrences.between(
                    dtstart.replace(hour=0, minute=0, second=0),
                    dtlast,
                    dtstart=booking.dtstart,
                    inc=True
                )

                for old_date in old_dates:
                    old_date_start = datetime.combine(
                        old_date.date(), booking.dtstart.time(), booking.dtstart.tzinfo)
                    old_date_end = datetime.combine(
                        old_date.date(), booking.dtend.time(), booking.dtend.tzinfo)
                    print("{} - {} | {} - {}".format(new_date_start,
                                                     new_date_end, old_date_start, old_date_end))
                    if (
                        timespan_conflict(
                            new_date_start, new_date_end, old_date_start, old_date_end)
                    ):
                        print('ho')
                        client_tz = get_current_timezone()
                        old_date_start = old_date_start.astimezone(client_tz)
                        old_date_end = old_date_end.astimezone(client_tz)
                        conflicts.append(
                            _('There is a conflict with in {} at {} to {}'.format(
                                workshop.name, old_date_start.strftime('%c'), old_date_end.strftime('%c')))
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
        if not self.errors:
            occurrences = WorkshopBooking.build_occurrences(
                recurrences.occurrences(), dtstart, dtend)
            self.occurrences = occurrences['occurrences']
            self.dtlast = occurrences['dtlast']
            conflicts = []
            for workshop in self.cleaned_data['workshops']:
                conflicts = conflicts + self._find_conflicts(
                    workshop, dtstart, self.dtlast, self.occurrences)

            if conflicts:
                raise forms.ValidationError(
                    conflicts
                )

            return recurrences

    def save(self, *args, commit=True, **kwargs):
        self.new_booking = super(WorkshopBookingForm, self).save(
            commit=False, *args, **kwargs)
        self.new_booking.organizer = self.request.actor
        self.new_booking.created_by = self.request.user
        self.new_booking.updated_by = self.request.user
        self.new_booking.recurrences.dtstart = self.new_booking.dtstart
        if self.dtlast is None:
            self.new_booking.dtlast = self.new_booking.dtend
        else:
            self.new_booking.dtlast = self.dtlast

        self.new_booking.save()
        self.save_m2m()
        return self.new_booking


class WorkshopContractForm(forms.ModelForm):
    def __init__(self, workshop, request, *args, **kwargs):
        super(WorkshopContractForm, self).__init__(*args, **kwargs)
        self.request = request
        self.workshop = workshop
        self.fields['payment_method'].queryset = workshop.contract_procedure.payment_methods.select_subclasses(
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
        self.fields['equipment'].queryset = WorkshopEquipment.objects.filter(
            workshop__contract_procedure=workshop.contract_procedure)

        if self.fields['price_profile'].queryset:
            self.initial['price_profile'] = self.fields['price_profile'].queryset[0]
            self.initial['payment_method'] = self.fields['payment_method'].queryset[0]

    def clean(self):
        data = super(WorkshopContractForm, self).clean()
        address = self.request.actor.address
        if (address.street is None or address.street_number is None or address.postal_code is None or address.city is None) and (
            self.workshop.base_price.value != Decimal(
                '0') and (self.cleaned_data['price_profile'] and self.cleaned_data['price_profile'].discount != Decimal('100'))
        ):
            raise forms.ValidationError(
                _('to create bookings you need to set your billing address'), code='address-not-set')

    class Meta:
        model = WorkshopContract
        fields = ['price_profile', 'payment_method', 'equipment', ]
        help_texts = {
            'price_profile': _('Available discounts granted to certain groups and entities. The discounts will be applied to the base prices below.')
        }


class WorkshopContractFormManager():
    def __init__(self, workshop, request):
        self.request = request
        self.workshop = workshop

        self.workshop_contract_form = WorkshopContractForm(
            self.workshop,
            self.request,
            data=self.request.POST
        ) if request.POST else WorkshopContractForm(self.workshop, self.request)
        self.booking_form = WorkshopBookingForm(
            self.workshop,
            self.request,
            data=self.request.POST,
            files=self.request.FILES
        ) if self.request.POST else WorkshopBookingForm(self.workshop, self.request)

    @property
    def occurrences(self):
        return self.booking_form.get_occurrences()

    def get_forms(self):
        return {
            'workshop_contract_form': self.workshop_contract_form,
            'booking_form': self.booking_form,
        }

    def is_valid(self):
        return (
            self.workshop_contract_form.is_valid() and
            self.booking_form.is_valid()
        )

    def save(self, commit=True):
        user = self.request.user
        actor = self.request.actor
        new_workshop_contract = self.workshop_contract_form.save(commit=False)
        new_workshop_contract.creditor = self.workshop.owner
        new_workshop_contract.debitor = actor
        new_workshop_contract.created_by = user
        new_workshop_contract.contract_procedure = self.workshop.contract_procedure
        new_workshop_contract.terms_and_conditions = self.workshop.contract_procedure.terms_and_conditions
        new_booking = self.booking_form.save()
        new_workshop_contract.booking = new_booking

        if commit:
            new_workshop_contract.save()
            self.workshop_contract_form.save_m2m()
        return new_workshop_contract


WorkshopPriceFormset = inlineformset_factory(
    Workshop,
    WorkshopPrice,
    form=PriceForm,
    extra=0,
    min_num=1,
    max_num=1,
    can_order=False,
)


class WorkshopEquipmentForm(forms.ModelForm):
    class Meta:
        model = WorkshopEquipment
        fields = ['name', 'quantity',
                  'thumbnail_original', ]


class OverridenBaseFormset(BaseInlineFormSet):
    @property
    def empty_form(self):
        form = self.form(
            auto_id=self.auto_id,
            prefix=self.add_prefix(str(0)),
            empty_permitted=True,
            use_required_attribute=False,
            **self.get_form_kwargs(None)
        )
        self.add_fields(form, None)
        return form


WorkshopEquipmentPriceFormset = inlineformset_factory(
    WorkshopEquipment,
    WorkshopEquipmentPrice,
    form=PriceForm,
    formset=OverridenBaseFormset,
    extra=1,
    min_num=1,
    max_num=1,
    can_order=False,
)


class BaseWorkshopEquipmentFormset(BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super(BaseWorkshopEquipmentFormset, self).__init__(*args, **kwargs)
        self.nested_empty_form = None
        self.nested_empty_management_form = None

    def add_fields(self, form, index):
        super(BaseWorkshopEquipmentFormset, self).add_fields(form, index)

        # save the formset in the 'nested' property
        form.nested = WorkshopEquipmentPriceFormset(
            instance=form.instance,
            data=form.data if form.is_bound else None,
            files=form.files if form.is_bound else None,
            prefix='equipment-price-%s-%s' % (
                form.prefix,
                WorkshopEquipmentPriceFormset.get_default_prefix(),
            )
        )

        self.nested_empty_form = form.nested.empty_form
        self.nested_empty_management_form = form.nested.management_form

    def is_valid(self):
        result = super(BaseWorkshopEquipmentFormset, self).is_valid()
        if self.is_bound:
            for form in self.forms:
                if hasattr(form, 'nested'):
                    result = result and form.nested.is_valid()
        return result

    def save(self, commit=True):
        result = super(BaseWorkshopEquipmentFormset, self).save(commit=False)
        for form in self.forms:
            if hasattr(form, 'nested'):
                form.nested.instance = form.instance
                if self._should_delete_form(form):
                    form.instance.price = None
                    form.instance.save()
                    WorkshopEquipmentPrice.objects.filter(
                        equipment_ptr=form.instance.pk).delete()
                else:
                    form.save()
                    first = True
                    for nested_form in form.nested.save(commit=True):
                        if first:
                            first = False
                            form.instance.price = nested_form.price_ptr
                            form.instance.save()
            else:
                form.save()
        super(BaseWorkshopEquipmentFormset, self).save(commit=True)
        return result


WorkshopEquipmentFormset = inlineformset_factory(
    Workshop,
    WorkshopEquipment,
    formset=BaseWorkshopEquipmentFormset,
    form=WorkshopEquipmentForm,
    min_num=0,
    extra=0,


)
