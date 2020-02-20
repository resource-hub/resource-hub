import uuid

from django.db import models

from resource_hub.core.models import (Actor, BaseContractProcedure, Contract, Gallery,
                                      Location)
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from recurrence.fields import RecurrenceField


class VenueContractProcedure(BaseContractProcedure):
    price_per_h = models.DecimalField(
        null=True,
        blank=True,
        max_digits=8,
        decimal_places=2,
    )
    max_price_per_d = models.DecimalField(
        null=True,
        blank=True,
        max_digits=8,
        decimal_places=2,
    )
    equipment = models.ManyToManyField(
        'Equipment',
        blank=True,
    )


class Venue(models.Model):
    """describing locations."""

    # Fields
    name = models.CharField(max_length=128)
    description = models.TextField()
    location = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
    )
    thumbnail_original = models.ImageField(
        null=False,
        blank=True,
        upload_to='images/',
    )
    thumbnail = ImageSpecField(
        source='thumbnail_original',
        processors=[
            ResizeToFill(400, 400),
        ],
        format='JPEG',
        options={
            'quality': 70,
        }
    )
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.SET_NULL,
        null=True
    )
    bookable = models.BooleanField(
        default=True,
    )
    booking_procedure = models.OneToOneField(
        VenueContractProcedure,
        null=True,
        on_delete=models.SET_NULL
    )
    created_at = models.DateField(
        auto_now=True,
    )
    owner = models.ForeignKey(
        Actor,
        on_delete=models.CASCADE
    )

    # Metadata
    class Meta:
        ordering = ['name']

    # Methods
    def __str__(self):
        return self.name


class EventTag(models.Model):
    name = models.CharField(max_length=64)

    # Metadata
    class Meta:
        ordering = ['name']

    # Methods
    def __str__(self):
        return self.name


class EventCategory(models.Model):
    name = models.CharField(max_length=64)

    # Metadata
    class Meta:
        ordering = ['name']

    # Methods
    def __str__(self):
        return self.name


class Event(models.Model):
    # fields
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
    )
    name = models.CharField(
        max_length=128,
    )
    description = models.CharField(
        max_length=128,
    )
    start = models.TimeField()
    end = models.TimeField()
    organizer = models.ForeignKey(
        Actor,
        on_delete=models.CASCADE,
        related_name='event_actor'
    )
    tags = models.ManyToManyField(
        EventTag,
    )
    category = models.ForeignKey(
        EventCategory,
        on_delete=models.SET_NULL,
        null=True
    )
    venue = models.ForeignKey(
        Venue,
        on_delete=models.CASCADE
    )
    is_public = models.BooleanField()
    recurrences = RecurrenceField(
        null=False,
    )
    thumbnail_original = models.ImageField(
        null=False,
        blank=True,
        upload_to='images/'
    )
    thumbnail = ImageSpecField(
        source='thumbnail_original',
        processors=[ResizeToFill(300, 300)],
        format='JPEG',
        options={'quality': 70},
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    created_by = models.ForeignKey(
        Actor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_created_by',
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        Actor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_updated_by',
    )

    # Metadata
    class Meta:
        ordering = ['name']

    # Methods
    def __str__(self):
        return self.name


class Equipment(models.Model):
    name = models.CharField(
        max_length=128,
    )
    price = models.DecimalField(
        max_digits=13,
        decimal_places=2,
    )


class VenueUsageContract(Contract):
    event = models.OneToOneField(
        Event,
        on_delete=models.PROTECT,
    )
    equipment = models.ManyToManyField(
        Equipment,
    )
