import uuid
from datetime import datetime

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q
from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from recurrence.fields import RecurrenceField
from resource_hub.core.fields import (CustomManyToManyField,
                                      MultipleChoiceArrayField)
from resource_hub.core.models import (Actor, BaseAsset, BaseModel, Claim,
                                      Contract, ContractProcedure, Gallery,
                                      Location, Notification, Price)
from resource_hub.core.utils import get_valid_slug, language


class VenueContractProcedure(ContractProcedure):
    venues = models.ManyToManyField(
        'Venue',
        verbose_name=_('Venues'),
    )

    @property
    def type_name(self):
        return _('Venue contract procedure')

    @property
    def form_link(self):
        return reverse('control:venues_contract_procedures_create')

    @property
    def edit_link(self):
        return reverse('control:venues_contract_procedures_edit', kwargs={'pk': self.pk})


def get_default_usage():
    return [Venue.USAGE_TYPE.OTHER]


class Venue(BaseAsset):
    """describing locations."""
    class USAGE_TYPE:
        OTHER = 'o'
        WORKSHOP = 'w'

    USAGE_TYPES = [
        (USAGE_TYPE.OTHER, _('other')),
        (USAGE_TYPE.WORKSHOP, _('workshop')),
    ]
    # Fields
    contract_procedure = models.ForeignKey(
        ContractProcedure,
        on_delete=models.PROTECT,
        verbose_name=_('Contract procedure'),
    )
    size = models.PositiveIntegerField(
        verbose_name=_('Room size (squaremeters)'),
        default=10,
    )
    usage_types = MultipleChoiceArrayField(
        models.CharField(
            choices=USAGE_TYPES,
            max_length=3,
        ),
        default=get_default_usage,
        verbose_name=_('Usage types'),
        help_text=_('Describe which activites are possible'),
    )
    bookable = models.BooleanField(
        default=True,
        verbose_name=_('Bookable?'),
    )
    owner = models.ForeignKey(
        Actor,
        on_delete=models.CASCADE,
        verbose_name=_('Owner'),
        help_text=_(
            'All available roles, be cautious when chosing a different role than your current.')

    )

    # Metadata
    class Meta:
        ordering = ['name']
        unique_together = ['name', 'location']

    # Methods
    def __str__(self):
        return '{}: {} ({})'.format(self.name, self.price, self.location.name)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = get_valid_slug(
                self, self.name, Q(location=self.location))
        super(Venue, self).save(*args, **kwargs)


class VenuePrice(Price):
    venue_ptr = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        related_name='venue_price'
    )


class EventTag(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_('Name'),
    )

    # Metadata
    class Meta:
        ordering = ['name']

    # Methods
    def __str__(self):
        return self.name


class EventCategory(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
        verbose_name=_('Name'),
    )

    # Metadata
    class Meta:
        ordering = ['name']

    # Methods
    def __str__(self):
        return self.name


class Event(BaseModel):
    # fields
    slug = models.SlugField(
        unique=True,
        db_index=True,
        max_length=50,
        verbose_name=_('Slug'),
    )
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('UUID'),
    )
    name = models.CharField(
        max_length=128,
        verbose_name=_('Name'),
    )
    description = models.CharField(
        max_length=128,
        verbose_name=_('Description'),
    )
    dtstart = models.DateTimeField(
        verbose_name=_('Start'),

    )
    dtend = models.DateTimeField(
        verbose_name=_('End'),

    )
    dtlast = models.DateTimeField()
    organizer = models.ForeignKey(
        Actor,
        on_delete=models.CASCADE,
        related_name='event_actor',
        verbose_name=_('Organizer'),
    )
    tags = models.ManyToManyField(
        EventTag,
        blank=True,
        verbose_name=_('Tags'),
    )
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Category'),
    )
    venues = CustomManyToManyField(
        Venue,
        verbose_name=_('Venues'),
    )
    is_public = models.BooleanField(
        default=True,
        blank=True,
        verbose_name=_('Public?'),
    )
    recurrences = RecurrenceField(
        null=False,
        blank=True,
        include_dtstart=True,
        verbose_name=_('Recurrences'),
    )
    thumbnail_original = models.ImageField(
        null=False,
        upload_to='images/',
        verbose_name=_('Thumbnail'),
    )
    thumbnail = ImageSpecField(
        source='thumbnail_original',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 70},
    )
    updated_by = models.ForeignKey(
        Actor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_updated_by',
        verbose_name=_('Updated by'),
    )
    # Metadata

    class Meta:
        ordering = ['name']

    # Methods
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = get_valid_slug(self, self.name)
        super(Event, self).save(*args, **kwargs)

    @classmethod
    def build_occurrences(cls, dates: list, dtstart, dtend) -> dict:
        result = {
            'occurrences': [],
            'dtlast': None
        }
        for date in dates:
            # get last occurrence and apply times to dates

            occurrence_start = datetime.combine(
                date.date(), dtstart.time(), dtstart.tzinfo)
            occurrence_end = datetime.combine(
                date.date(), dtend.time(), dtend.tzinfo)
            result['occurrences'].append(
                (occurrence_start, occurrence_end)
            )
            result['dtlast'] = occurrence_end

        return result

    @property
    def occurrences(self) -> list:
        return self.build_occurrences(self.recurrences.occurrences(), self.dtstart, self.dtend)['occurrences']


class Equipment(models.Model):
    # fields
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name=_('Name'),
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.PROTECT,
        verbose_name=_('Venue'),
        related_name='equipment',
    )
    thumbnail_original = models.ImageField(
        verbose_name=_('Thumbnail'),

    )
    thumbnail = ImageSpecField(
        source='thumbnail_original',
        processors=[ResizeToFill(200, 200)],
        format='JPEG',
        options={'quality': 70},
    )
    thumbnail_large = ImageSpecField(
        source='thumbnail_original',
        processors=[ResizeToFill(400, 400)],
        format='JPEG',
        options={'quality': 90},
    )
    price = models.ForeignKey(
        Price,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('Price'),
    )
    quantity = models.IntegerField(
        verbose_name=_('Quantity'),
    )

    # methods
    def __str__(self):
        return '{}@{} ({})'.format(self.name, self.venue.name, self.price)


class EquipmentPrice(Price):
    equipment_ptr = models.ForeignKey(
        Equipment,
        on_delete=models.PROTECT,
        related_name='equipment_price'
    )


class EquipmentBooking(BaseModel):
    # fields
    contract = models.ForeignKey(
        'VenueContract',
        on_delete=models.PROTECT,
        verbose_name=_('Contract'),
        related_name='equipment_bookings',
    )
    equipment = models.ForeignKey(
        'Equipment',
        on_delete=models.PROTECT,
        verbose_name=_('Equipment'),
        related_name='equipment_bookings',
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Quantity'),
    )


class VenueContract(Contract):
    event = models.OneToOneField(
        Event,
        on_delete=models.PROTECT,
        verbose_name=_('Event'),
    )
    equipment = models.ManyToManyField(
        Equipment,
        blank=True,
        through='EquipmentBooking',
        verbose_name=_('Equipment'),
        help_text=_('Services or additional equipment for the venue'),

    )

    # attributes
    @property
    def verbose_name(self):
        return _('Venue booking')

    @property
    def overview(self):
        return render_to_string(
            'venues/_contract_overview.html',
            context={
                'contract': self,
            }
        )

    # methods
    def claim_factory(self, **kwargs):
        super(VenueContract, self).claim_factory(**kwargs)
        occurrences = kwargs.get('occurrences', None)
        if not occurrences:
            raise ValueError('no occurrences passed')
        net_total = 0
        for venue in self.event.venues.all():
            for occurrence in occurrences:
                start = occurrence[0]
                end = occurrence[1]
                delta = ((end - start).total_seconds())/3600
                claim = Claim.build(
                    contract=self,
                    item='{}@{}'.format(
                        self.event.name,
                        venue.name
                    ),
                    quantity=delta,
                    unit='h',
                    price=venue.base_price,
                    start=start,
                    end=end,
                )
                net_total += claim.net

        for booking in self.equipment_bookings.all():
            for occurrence in occurrences:
                equipment = booking.equipment
                Claim.build(
                    contract=self,
                    item='{}@{}'.format(
                        equipment.name,
                        equipment.venue.name,
                    ),
                    quantity=booking.quantity,
                    unit='u',
                    price=equipment.price,
                    start=occurrence[0],
                    end=occurrence[1],
                )

        self.create_fee_claims(
            net_total, venue.base_price.currency, start, end)

    # state setters

    def purge(self):
        super(VenueContract, self).purge()
        self.event.soft_delete()

    def set_waiting(self, request):
        super(VenueContract, self).set_waiting(request)
        with language(self.creditor.language):
            Notification.build(
                type_=Notification.TYPE.CONTRACT,
                sender=self.debitor,
                recipient=self.creditor,
                header=_('%(debitor)s created Event: %(event)s') % {
                    'debitor': self.debitor,
                    'event': self.event.name
                },
                link=reverse('control:finance_contracts_manage_details',
                             kwargs={'pk': self.pk}),
                level=Notification.LEVEL.MEDIUM,
                message='',
                target=self,
            )

    def set_terminated(self, initiator):
        super(VenueContract, self).set_terminated(initiator)
        self.event.soft_delete()
