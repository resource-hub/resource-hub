from django.db import models
from core.models import Location, Actor


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
