from core.models import User, Actor
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['id', 'name', ]


class ActorSerializerMinimal(serializers.ModelSerializer):
    thumbnail = serializers.ImageField()

    class Meta:
        model = Actor
        fields = ['id', 'name', 'thumbnail']
