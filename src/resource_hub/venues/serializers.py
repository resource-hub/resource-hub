from django.urls import reverse

from resource_hub.core.models import Actor, Organization, User
from resource_hub.core.serializers import ActorSerializer, LocationSerializer
from rest_framework import serializers
from resource_hub.venues.models import Event, Venue


class VenueSerializer(serializers.ModelSerializer):
    owner = ActorSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    thumbnail = serializers.ImageField()
    room_link = serializers.SerializerMethodField()

    def get_room_link(self, obj):
        return reverse('venues:room_details', kwargs={'room_id': obj.id})

    class Meta:
        model = Venue
        fields = ['id', 'name', 'description', 'room_link', 'location',
                  'thumbnail', 'owner']


# class EventSerializer(serializers.ModelSerializer):
#     organizer = ActorSerializer(read_only=True)

#     def to_representation(self, instance):


#     class Meta:
#         model = Event
#         fields = ['id', 'name', 'description', 'organizer', ]
