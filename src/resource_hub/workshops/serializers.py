from django.urls import reverse
from resource_hub.core.serializers import ActorSerializer, LocationSerializer
from resource_hub.workshops.models import Workshop
from rest_framework import serializers


class WorkshopSerializer(serializers.ModelSerializer):
    owner = ActorSerializer(read_only=True)
    location = LocationSerializer(read_only=True)
    thumbnail = serializers.SerializerMethodField()
    workshop_link = serializers.SerializerMethodField()

    def get_workshop_link(self, obj):
        return reverse('workshops:workshop_details', kwargs={'workshop_slug': obj.slug, 'location_slug': obj.location.slug})

    def get_thumbnail(self, obj):
        return obj.thumbnail.url

    class Meta:
        model = Workshop
        fields = ['id', 'name', 'description', 'workshop_link', 'location',
                  'thumbnail', 'owner']
