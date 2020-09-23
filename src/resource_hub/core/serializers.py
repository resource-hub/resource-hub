from django.conf import settings
from django.shortcuts import reverse

from resource_hub.core.models import (Actor, Address, Contract, Location,
                                      Notification, User)
from rest_framework import serializers

from .models import NotificationAttachment, OrganizationMember


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return '{} {}'.format(obj.first_name, obj.last_name)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'full_name']


class ActorSerializer(serializers.ModelSerializer):
    thumbnail = serializers.SerializerMethodField()

    def get_thumbnail(self, obj):
        return obj.thumbnail.url

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


class ContractSerializer(serializers.ModelSerializer):
    type_name = serializers.SerializerMethodField()
    state_display = serializers.SerializerMethodField()
    created_at = serializers.SerializerMethodField()
    creditor = ActorSerializer()
    debitor = ActorSerializer()
    link = serializers.SerializerMethodField()

    def get_type_name(self, obj):
        return obj.verbose_name

    def get_created_at(self, obj):
        return obj.created_at.strftime('%m.%d.%Y %H:%m:%S')

    def get_state_display(self, obj):
        return obj.get_state_display()

    def get_link(self, obj):
        return reverse('control:finance_contracts_manage_details', kwargs={'pk': obj.pk})

    class Meta:
        model = Contract
        fields = ['type_name', 'state', 'state_display', 'creditor',
                  'debitor', 'link', 'created_at', ]


class LocationSerializer(serializers.ModelSerializer):
    address = AddressSerializer()
    owner = ActorSerializer()
    # thumbnail = serializers.ImageField(use_url=False)
    thumbnail = serializers.SerializerMethodField()
    location_link = serializers.SerializerMethodField()

    def get_location_link(self, obj):
        return reverse('core:locations_profile', kwargs={'slug': obj.slug})

    def get_thumbnail(self, obj):
        return obj.thumbnail.url

    class Meta:
        model = Location
        fields = ['name', 'latitude',
                  'longitude', 'address', 'owner', 'thumbnail', 'location_link', ]


class AttachmentSerializer(serializers.ModelSerializer):
    path = serializers.SerializerMethodField()
    filename = serializers.SerializerMethodField()

    def get_path(self, obj):
        return obj.file.path

    def get_filename(self, obj):
        return obj.file.filename

    class Meta:
        model = NotificationAttachment
        fields = ['pk', 'path', 'filename', ]


class NotificationSerializer(serializers.ModelSerializer):
    sender = ActorSerializer()
    typ = serializers.SerializerMethodField()
    attachments = AttachmentSerializer(many=True, read_only=True)

    def get_typ(self, obj):
        return obj.get_type_icon(obj.typ)

    class Meta:
        model = Notification
        fields = ['pk', 'typ', 'sender', 'recipient', 'header', 'message', 'link',
                  'level', 'is_read', 'attachments', 'created_at', ]


class OrganizationMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationMember
        fields = ['pk', 'role', 'user', 'organization', ]
