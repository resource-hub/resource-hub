from django import forms
from django.db.models import Q
from django.forms import inlineformset_factory
from django.utils.timezone import get_current_timezone
from django.utils.translation import gettext_lazy as _

from resource_hub.core.fields import HTMLField
from resource_hub.core.forms import (ContractProcedureForm, FormManager,
                                     GalleryImageFormSet, PriceForm,
                                     PriceProfileFormSet)
from resource_hub.core.models import Gallery, Price, PriceProfile
from resource_hub.core.utils import get_authorized_actors, timespan_conflict

from .models import (Item, ItemBooking, ItemContract, ItemContractProcedure,
                     ItemPrice)


class ItemContractProcedureForm(ContractProcedureForm):
    class Meta(ContractProcedureForm.Meta):
        model = ItemContractProcedure
        fields = [*ContractProcedureForm.Meta.fields, 'self_pickup_group', ]

    def save(self, commit=True, **kwargs):
        new_item_contract_procedure = super(
            ItemContractProcedureForm, self).save(commit=False, **kwargs)
        new_item_contract_procedure.owner = self.request.actor

        if commit:
            new_item_contract_procedure.save()
            self.save_m2m()
        return new_item_contract_procedure


class ItemForm(forms.ModelForm):
    def __init__(self, user, actor, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.user = user
        self.actor = actor
        contract_procedures = ItemContractProcedure.objects.filter(
            owner=self.actor)
        self.fields['contract_procedure'].queryset = contract_procedures

        self.fields['owner'].queryset = get_authorized_actors(
            self.user,
        )

        # inital values
        self.initial['owner'] = self.actor
        if contract_procedures:
            self.initial['contract_procedure'] = contract_procedures[0]

        # self._update_attrs({
        #     'contract_procedure': {'class': 'booking-item required'},
        # })

    description = HTMLField()

    class Meta:
        model = Item
        fields = ['custom_id', 'name', 'description', 'contract_procedure', 'manufacturer', 'model', 'serial_no', 'location', 'location_code', 'unit', 'maximum_duration', 'self_pickup', 'damages', 'category', 'instructions', 'attachment',
                  'thumbnail_original', 'owner', 'donation', 'original_owner', 'purchase_price', 'replacement_price', ]
        help_texts = {
            'bookable': _('Do you want to use the platform\'s booking logic?'),
        }

    def _update_attrs(self, fields):
        for field, val in fields.items():
            self.fields[field].widget.attrs.update(val)

    def save(self, *args, **kwargs):
        commit = kwargs.get('commit', True)
        kwargs['commit'] = False
        new_item = super(ItemForm, self).save(*args, **kwargs)
        new_item.owner = self.actor
        if commit:
            new_item.save()
        return new_item


ItemPriceFormset = inlineformset_factory(
    Item,
    ItemPrice,
    form=PriceForm,
    extra=0,
    min_num=1,
    can_order=True,
)


class ItemFormManager(FormManager):
    def __init__(self, user, actor, data=None, files=None, instance=None):
        gallery_instance = instance.gallery if instance else None
        if data:
            self.forms = {
                'item_form': ItemForm(
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
                'price_formset': ItemPriceFormset(
                    data=data,
                    instance=instance,
                ),
            }
        else:
            self.forms = {
                'item_form': ItemForm(
                    user,
                    actor,
                    instance=instance,
                ),
                'gallery_formset': GalleryImageFormSet(
                    instance=gallery_instance,
                ),
                'price_formset': ItemPriceFormset(
                    instance=instance,
                ),
            }

    def save(self):
        new_item = self.forms['item_form'].save(commit=False)
        first = True
        if new_item.gallery is None:
            new_item.gallery = Gallery.objects.create()

        self.forms['gallery_formset'].instance = new_item.gallery
        self.forms['gallery_formset'].save()
        self.forms['price_formset'].instance = new_item
        for price in self.forms['price_formset'].save():
            price.item = new_item
            if first:
                new_item.base_price = price
                first = False
        new_item.save()
        return new_item


class ItemContractProcedureFormManager(FormManager):
    def __init__(self, request, instance=None):
        if request.POST:
            self.forms = {
                'contract_procedure_form': ItemContractProcedureForm(request, data=request.POST, files=request.FILES, instance=instance),
                'price_profile_form_set': PriceProfileFormSet(data=request.POST, files=request.FILES, instance=instance)
            }
        else:
            self.forms = {
                'contract_procedure_form': ItemContractProcedureForm(request, instance=instance),
                'price_profile_form_set': PriceProfileFormSet(instance=instance)
            }

    def save(self):
        new_item_contract_procedure = self.forms['contract_procedure_form'].save(
        )
        for form in self.forms['price_profile_form_set'].save(commit=False):
            form.contract_procedure = new_item_contract_procedure
            form.save()

        for deleted_form in self.forms['price_profile_form_set'].deleted_objects:
            deleted_form.delete()

        return new_item_contract_procedure


class ItemContractForm(forms.ModelForm):
    def __init__(self, item, request, *args, **kwargs):
        super(ItemContractForm, self).__init__(*args, **kwargs)
        self.request = request
        self.fields['payment_method'].queryset = item.contract_procedure.payment_methods.select_subclasses(
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
        data = super(ItemContractForm, self).clean()
        address = self.request.actor.address
        if address.street is None or address.street_number is None or address.postal_code is None or address.city is None:
            raise forms.ValidationError(
                _('to create bookings you need to set your billing address'), code='address-not-set')

    class Meta:
        model = ItemContract
        fields = ['price_profile', 'payment_method', 'note', ]
        help_texts = {
            'price_profile': _('Available discounts granted to certain groups and entities. The discounts will be applied to the base prices below.')
        }


class ItemBookingForm(forms.ModelForm):
    def __init__(self, item, *args, **kwargs):
        super(ItemBookingForm, self).__init__(*args, **kwargs)
        self.item = item

    def clean(self):
        cleaned_data = super().clean()
        dtstart = cleaned_data.get('dtstart')
        dtend = cleaned_data.get('dtend')
        quantity = cleaned_data.get('quantity')
        if dtstart and dtend and quantity:
            query = Q(dtend__gt=dtstart)
            query.add(
                Q(dtstart__lt=dtend),
                Q.AND
            )
            query.add(Q(item=self.item), Q.AND)
            bookings = ItemBooking.objects.filter(query)
            conflicts = []
            for booking in bookings:
                delta = self.item.quantity - booking.quantity - quantity
                if timespan_conflict(booking.dtstart, booking.dtend, dtstart, dtend) and delta < 0:
                    client_tz = get_current_timezone()
                    booking_start = booking.dtstart.astimezone(client_tz)
                    booking_end = booking.dtend.astimezone(client_tz)
                    conflicts.append(
                        _('There is a missing quantity of {} with booking on {} to {}'.format(
                            delta, booking_start.strftime('%c'), booking_end.strftime('%c')))
                    )
            if conflicts:
                raise forms.ValidationError(conflicts)

    class Meta:
        model = ItemBooking
        fields = ['dtstart', 'dtend', 'quantity', ]


class ItemContractFormManager():
    def __init__(self, item, request):
        self.request = request
        self.item = item

        self.item_contract_form = ItemContractForm(
            self.item,
            self.request,
            data=self.request.POST
        ) if request.POST else ItemContractForm(self.item, self.request)
        self.item_form = ItemBookingForm(
            self.item,
            data=self.request.POST,
        ) if self.request.POST else ItemBookingForm(self.item)

    def get_forms(self):
        return {
            'item_contract_form': self.item_contract_form,
            'item_form': self.item_form,
        }

    def is_valid(self):
        return (
            self.item_contract_form.is_valid() and
            self.item_form.is_valid()
        )

    def save(self, commit=True):
        user = self.request.user
        actor = self.request.actor
        new_item_contract = self.item_contract_form.save(commit=False)
        new_item_contract.creditor = self.item.owner
        new_item_contract.debitor = actor
        new_item_contract.created_by = user
        new_item_contract.contract_procedure = self.item.contract_procedure
        new_item_contract.terms_and_conditions = self.item.contract_procedure.terms_and_conditions
        item_booking = self.item_form.save(commit=False)
        item_booking.contract = new_item_contract
        item_booking.item = self.item

        if commit:
            new_item_contract.save()
            item_booking.save()
            self.item_contract_form.save_m2m()
        return new_item_contract
