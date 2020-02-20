from django.shortcuts import reverse

from resource_hub.core.models import Actor, Address, Location, User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'full_name']


class ActorSerializer(serializers.ModelSerializer):
    thumbnail = serializers.ImageField()

    class Meta:
        model = Actor
        fields = ['id', 'name', 'thumbnail']


class AddressSerializer(serializers.ModelSerializer):
    address_string = serializers.SerializerMethodField()

    def get_address_string(self, obj):
        return "{} {}, {} {}".format(obj.street, obj.street_number, obj.postal_code, obj.city)

    class Meta:
        model = Address
        fields = ['street', 'street_number',
                  'postal_code', 'city', 'address_string']


class LocationSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    owner = ActorSerializer()
    thumbnail = serializers.ImageField()
    location_link = serializers.SerializerMethodField()

    def get_location_link(self, obj):
        return reverse('core:locations_profile', kwargs={'location_id': obj.id})

    class Meta:
        model = Location
        fields = ['name', 'latitude',
                  'longitude', 'address', 'owner', 'thumbnail', 'location_link', ]
