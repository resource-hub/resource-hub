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


class WorkshopContractProcedure(ContractProcedure):
    workshops = models.ManyToManyField(
        'Workshop',
        verbose_name=_('Workshop'),
    )

    @property
    def type_name(self):
        return _('Workshop contract procedure')

    @property
    def form_link(self):
        return reverse('control:workshops_contract_procedures_create')

    @property
    def edit_link(self):
        return reverse('control:workshops_contract_procedures_edit', kwargs={'pk': self.pk})


class Workshop(BaseAsset):

    # Fields
    contract_procedure = models.ForeignKey(
        ContractProcedure,
        on_delete=models.PROTECT,
        verbose_name=_('Contract procedure'),
    )
    workplaces = models.PositiveIntegerField(
        default=1,
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
        unique_together = ['name', 'location', ]

    # Methods
    def __str__(self):
        return '{}: {} ({})'.format(self.name, self.base_price, self.location.name)

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = get_valid_slug(
                self, self.name, Q(location=self.location))
        super(Workshop, self).save(*args, **kwargs)


class WorkshopPrice(Price):
    workshop_ptr = models.ForeignKey(
        Workshop,
        on_delete=models.PROTECT,
        related_name='workshop_price'
    )


class WorkshopBooking(BaseModel):
    # fields
    dtstart = models.DateTimeField(
        verbose_name=_('Start'),
    )
    dtend = models.DateTimeField(
        verbose_name=_('End'),

    )
    dtlast = models.DateTimeField()
    recurrences = RecurrenceField(
        null=False,
        blank=True,
        include_dtstart=True,
        verbose_name=_('Recurrences'),
    )
    workplaces = models.PositiveIntegerField(
        default=1,
    )
    workshops = CustomManyToManyField(
        Workshop,
        verbose_name=_('Workshop'),
    )
    # Methods

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


class WorkshopEquipment(models.Model):
    # fields
    name = models.CharField(
        max_length=128,
        unique=True,
        verbose_name=_('Name'),
    )
    workshop = models.ForeignKey(
        Workshop,
        on_delete=models.PROTECT,
        verbose_name=_('Workshop'),
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
        return '{}@{} ({})'.format(self.name, self.workshop.name, self.price)


class WorkshopEquipmentPrice(Price):
    equipment_ptr = models.ForeignKey(
        WorkshopEquipment,
        on_delete=models.PROTECT,
        related_name='equipment_price'
    )


class EquipmentBooking(BaseModel):
    # fields
    contract = models.ForeignKey(
        'WorkshopContract',
        on_delete=models.PROTECT,
        verbose_name=_('Contract'),
        related_name='equipment_bookings',
    )
    equipment = models.ForeignKey(
        'WorkshopEquipment',
        on_delete=models.PROTECT,
        verbose_name=_('WorkshopEquipment'),
        related_name='equipment_bookings',
    )
    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name=_('Quantity'),
    )


class WorkshopContract(Contract):
    booking = models.OneToOneField(
        WorkshopBooking,
        on_delete=models.PROTECT,
        verbose_name=_('Event'),
    )
    equipment = CustomManyToManyField(
        WorkshopEquipment,
        blank=True,
        through='EquipmentBooking',
        verbose_name=_('WorkshopEquipment'),
        help_text=_('Services or additional equipment for the workshop'),

    )

    # attributes
    @property
    def verbose_name(self):
        return _('Workshop booking')

    @property
    def overview(self):
        return render_to_string(
            'workshops/_contract_overview.html',
            context={
                'contract': self,
            }
        )

    # methods
    def claim_factory(self, **kwargs):
        super(WorkshopContract, self).claim_factory(**kwargs)
        occurrences = kwargs.get('occurrences', None)
        if not occurrences:
            raise ValueError('no occurrences passed')
        net_total = 0
        for workshop in self.booking.workshops.all():
            for occurrence in occurrences:
                start = occurrence[0]
                end = occurrence[1]
                delta = ((end - start).total_seconds())/3600
                claim = Claim.build(
                    contract=self,
                    item='{}'.format(
                        workshop.name
                    ),
                    quantity=delta,
                    unit='h',
                    price=workshop.base_price,
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
                        equipment.workshop.name,
                    ),
                    quantity=booking.quantity,
                    unit='u',
                    price=equipment.price,
                    start=occurrence[0],
                    end=occurrence[1],
                )

        self.create_fee_claims(
            net_total, workshop.base_price.currency, start, end)

    # state setters

    def purge(self):
        super(WorkshopContract, self).purge()
        self.booking.soft_delete()

    def set_waiting(self, request):
        super(WorkshopContract, self).set_waiting(request)
        with language(self.creditor.language):
            Notification.build(
                type_=Notification.TYPE.CONTRACT,
                sender=self.debitor,
                recipient=self.creditor,
                header=_('%(debitor)s created Booking') % {
                    'debitor': self.debitor,
                },
                link=reverse('control:finance_contracts_manage_details',
                             kwargs={'pk': self.pk}),
                level=Notification.LEVEL.MEDIUM,
                message='',
                target=self,
            )

    def set_terminated(self, initiator):
        super(WorkshopContract, self).set_terminated(initiator)
        self.booking.soft_delete()
