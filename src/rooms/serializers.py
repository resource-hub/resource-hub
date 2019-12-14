from rooms.models import Room, Event
from rest_framework import serializers

from core.models import Actor, User, Organization
from core.serializers import ActorSerializerMinimal


class RoomSerializer(serializers.ModelSerializer):
    owner = ActorSerializerMinimal(read_only=True)
    thumbnail = serializers.ImageField()

    class Meta:
        model = Room
        fields = ['name', 'description', 'location',
                  'price_per_h', 'max_price_per_d', 'thumbnail', 'owner']
