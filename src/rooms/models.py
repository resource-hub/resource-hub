from django.db import models
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


class EventCategory(models.Model):
    name = models.CharField(max_length=64)


class Event(models.Model):
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
    start = models.DateTimeField()
    end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_created_by'
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_updated_by'
    )


class EventException(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    is_rescheduled = models.BooleanField()
    is_canceled = models.BooleanField()
    start = models.DateTimeField()
    end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='event_exception_created_by'
    )
