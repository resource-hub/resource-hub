from django.urls import reverse

from rooms.models import Room, Event
from rest_framework import serializers

from core.models import Actor, User, Organization
from core.serializers import ActorSerializerMinimal, LocationSerializer


class RoomSerializer(serializers.ModelSerializer):
    owner = ActorSerializerMinimal(read_only=True)
    location = LocationSerializer(read_only=True)
    thumbnail = serializers.ImageField()
    room_link = serializers.SerializerMethodField()

    def get_room_link(self, obj):
        return reverse('rooms:room_details', kwargs={'room_id': obj.id})

    class Meta:
        model = Room
        fields = ['id', 'name', 'description', 'room_link', 'location',
                  'price_per_h', 'max_price_per_d', 'thumbnail', 'owner']
