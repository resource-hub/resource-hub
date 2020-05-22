from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from resource_hub.core.serializers import ActorSerializer, LocationSerializer
from rest_framework import serializers

from .models import Item, ItemBooking


class ItemSerializer(serializers.ModelSerializer):
    owner = ActorSerializer(read_only=True)
    location = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    href = serializers.SerializerMethodField()

    def get_location(self, obj):
        if obj.location.is_public:
            return LocationSerializer(obj.location).data
        return {'address': {'address_string': obj.location.address.postal_code}}

    def get_thumbnail(self, obj):
        return obj.thumbnail.url

    def get_href(self, obj):
        return reverse('items:details', kwargs={'item_slug': obj.slug, 'owner_slug': obj.owner.slug})

    class Meta:
        model = Item
        fields = ['id', 'name', 'description', 'href', 'location',
                  'thumbnail', 'owner']


class ItemBookingSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    start = serializers.SerializerMethodField()
    end = serializers.SerializerMethodField()

    def get_title(self, obj):
        return _('Quantity: {}'.format(obj.quantity))

    def get_start(self, obj):
        return obj.dtstart

    def get_end(self, obj):
        return obj.dtend

    class Meta:
        model = ItemBooking
        fields = ['pk', 'start', 'end', 'title', ]
