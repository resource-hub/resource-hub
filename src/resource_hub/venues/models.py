import uuid
from datetime import datetime

from django.db import models
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from recurrence.fields import RecurrenceField
from resource_hub.core.models import (Actor, BaseContractProcedure, Contract,
                                      Gallery, Location)


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
    slug = models.SlugField(
        db_index=True,
        max_length=50,
    )
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
    contract_procedure = models.OneToOneField(
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
        unique_together = ['name', 'location']

    # Methods
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.id:
            slug = slugify(self.name)
            try:
                Venue.objects.get(slug=slug, location=self.location)
                self.slug = slug + str(datetime.now().date())
            except Venue.DoesNotExist:
                self.slug = slug
        super(Venue, self).save(*args, **kwargs)


class EventTag(models.Model):
    name = models.CharField(
        max_length=64,
        unique=True,
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
    )

    # Metadata
    class Meta:
        ordering = ['name']

    # Methods
    def __str__(self):
        return self.name


class Event(models.Model):
    # fields
    slug = models.SlugField(
        unique=True,
        db_index=True,
        max_length=50,
    )
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
    dtstart = models.DateTimeField()
    dtend = models.DateTimeField()
    dtlast = models.DateTimeField()
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
    is_public = models.BooleanField(
        default=True,
        null=False,
    )
    recurrences = RecurrenceField(
        null=False,
        blank=True,
        include_dtstart=True,
    )
    thumbnail_original = models.ImageField(
        null=False,
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

    def save(self, *args, **kwargs):
        if not self.id:
            slug = slugify(self.name)
            try:
                Event.objects.get(slug=slug)
                self.slug = slug + str(datetime.now().date())
            except Event.DoesNotExist:
                self.slug = slug
        super(Event, self).save(*args, **kwargs)


class Equipment(models.Model):
    name = models.CharField(
        max_length=128,
        unique=True,
    )
    price = models.DecimalField(
        max_digits=13,
        decimal_places=2,
    )


class VenueContract(Contract):
    event = models.OneToOneField(
        Event,
        on_delete=models.PROTECT,
    )
    equipment = models.ManyToManyField(
        Equipment,
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
    def claim_factory(self):
        return
