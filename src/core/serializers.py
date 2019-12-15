from core.models import User, Actor, Location
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


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ['name', 'description', 'latitude', 'longitude', ]
