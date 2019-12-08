import uuid

from django.db import models
from recurrence.fields import RecurrenceField

from core.models import Location, Actor, User


class Room(models.Model):
    """ describing locations """

    # Fields
    name = models.CharField(max_length=128)
    description = models.TextField()
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    price_per_h = models.DecimalField(max_digits=8, decimal_places=2)
    max_price_per_d = models.DecimalField(max_digits=8, decimal_places=2)
    negiotiable = models.BooleanField()
    created_at = models.DateField(auto_now=True)
    owner = models.ForeignKey(Actor, on_delete=models.CASCADE)

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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=128)
    description = models.CharField(max_length=128)
    organizer = models.ForeignKey(
        Actor, on_delete=models.CASCADE, related_name='event_actor')
    tags = models.ManyToManyField(EventTag)
    category = models.ForeignKey(
        EventCategory, on_delete=models.SET_NULL, null=True)
    parent_event = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    is_public = models.BooleanField()
    is_recurring = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateTimeField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    recurrences = RecurrenceField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Actor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_created_by'
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        Actor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_updated_by'
    )

    # Metadata
    class Meta:
        ordering = ['start_date']

    # Methods
    def __str__(self):
        return self.name


class EventException(models.Model):
    # fields
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_rescheduled = models.BooleanField()
    is_canceled = models.BooleanField()
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        Actor,
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_exception_created_by'
    )

    # Metadata
    class Meta:
        ordering = ['start_date']

    # Methods
    def __str__(self):
        return self.name


# class RecurrenceRule(models.Model):
#     # constants
#     SUNDAY = 'SU'
#     MONDAY = 'MO'
#     TUESDAY = 'TU'
#     WEDNESDAY = 'WE'
#     THURSDAY = 'TH'
#     FRIDAY = 'FR'
#     SATURDAY = 'SA'

#     WEEKDAYS = [
#         (SUNDAY, _('Sunday')),
#         (MONDAY, _('Monday')),
#         (TUESDAY, _('Tuesday')),
#         (WEDNESDAY, _('Wednesdy')),
#         (THURSDAY, _('Thursday')),
#         (FRIDAY, _('Friday')),
#         (SATURDAY, _('Saturday')),
#     ]

#     FREQUENCY_TYPES = [
#         ('YEARLY', _('yearly')),
#         ('MONTHLY', _('monthly')),
#         ('WEEKLY', _('weekly')),
#         ('DAILY', _('daily')),
#         ('HOURLY', _('hourly')),
#     ]

#     # fields
#     event = models.OneToOneField(Event, on_delete=models.CASCADE)
#     frequency = models.CharField(choices=FREQUENCY_TYPES)
#     interval = models.IntegerField(null=True)

#     by_month = models.IntegerField(null=True)
#     by_month_day = models.IntegerField(null=True)
#     by_day = models.CharField(choices=WEEKDAYS)
#     by_set_pos = models.IntegerField(null=True)

#     count = models.IntegerField(null=True)
#     until = models.DateField(null=True)

#     # Metadata
#     class Meta:
#         ordering = ['event']

#     # Methods
#     def __str__(self):
#         return self.name
