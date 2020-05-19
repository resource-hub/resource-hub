from django.urls import reverse
from resource_hub.core.serializers import ActorSerializer, LocationSerializer
from rest_framework import serializers

from .models import Item


class ItemSerializer(serializers.ModelSerializer):
    owner = ActorSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    thumbnail = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()

    def get_href(self, obj):
        return reverse('items:details', kwargs={'item_slug': obj.slug, 'owner_slug': obj.owner.slug})

    def get_thumbnail(self, obj):
        return obj.thumbnail.url

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'href', 'location',
                  'thumbnail', 'owner']
