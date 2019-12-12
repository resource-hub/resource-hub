from rooms.models import Room, Event
from rest_framework import serializers

from core.models import Actor, User, Organization


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


class ActorSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    organization = OrganizationSerializer(read_only=True)

    class Meta:
        model = Actor
        fields = '__all__'


class RoomSerializer(serializers.ModelSerializer):
    owner = ActorSerializer(read_only=True)
    thumbnail = serializers.ImageField()

    class Meta:
        model = Room
        fields = ['name', 'description', 'location',
                  'price_per_h', 'max_price_per_d', 'thumbnail', 'owner']
