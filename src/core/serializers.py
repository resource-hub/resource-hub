from core.models import Actor, Address, Location, User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'full_name']


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'name', ]


class ActorSerializerMinimal(serializers.ModelSerializer):
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

    class Meta:
        model = Location
        fields = ['name', 'description', 'latitude', 'longitude', 'address', ]
