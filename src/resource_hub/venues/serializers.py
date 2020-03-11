from django.urls import reverse

from resource_hub.core.serializers import ActorSerializer, LocationSerializer
from resource_hub.venues.models import Venue
from rest_framework import serializers


class VenueSerializer(serializers.ModelSerializer):
    owner = ActorSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    thumbnail = serializers.ImageField()
    venue_link = serializers.SerializerMethodField()

    def get_venue_link(self, obj):
        return reverse('venues:venue_details', kwargs={'venue_slug': obj.slug, 'location_slug': obj.location.slug})

    class Meta:
        model = Venue
        fields = ['id', 'name', 'description', 'venue_link', 'location',
                  'thumbnail', 'owner']