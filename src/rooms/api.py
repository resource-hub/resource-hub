import re

from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _

from rest_framework import status, filters, generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework import exceptions
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.models import Room, Event
from rooms.serializers import RoomSerializer, EventSerializer


'''
Thanks to https://stackoverflow.com/questions/41129921/validate-an-iso-8601-datetime-string-in-python
'''

regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
match_iso8601 = re.compile(regex).match


def is_valid_iso8601(val):
    try:
        if match_iso8601(val) is not None:
            return True
    except:
        pass
    return False


@authentication_classes([])
@permission_classes([])
class Rooms(generics.ListCreateAPIView):
    http_method_names = ['get']
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    queryset = Room.objects.all()
    serializer_class = RoomSerializer


@authentication_classes([])
@permission_classes([])
class RoomEvents(generics.ListCreateAPIView):
    http_method_names = ['get']
    serializer_class = EventSerializer

    def get_queryset(self):
        start = self.request.query_params.get('start', None)
        end = self.request.query_params.get('end', None)
        room_id = self.kwargs['room_id']

        if start is None or end is None:
            raise exceptions.NotFound(
                detail=_('start or end parameter not set'))

        if not is_valid_iso8601(start) or not is_valid_iso8601(end):
            raise exceptions.ParseError(
                detail=_('start or end parameter not valid iso_8601 string'))

        try:
            queryset = Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise exception.NotFound(
                detail=_('No room corresponds to the given id'))

        queryset = Event.objects.filter(room=room_id)

        return queryset
