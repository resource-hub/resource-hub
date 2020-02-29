import re
from datetime import datetime

import dateutil.parser
from django.db.models import Q
from django.forms.models import model_to_dict
from django.utils.translation import ugettext_lazy as _

from resource_hub.venues.models import Event, Venue
from resource_hub.venues.serializers import VenueSerializer
from rest_framework import exceptions, filters, generics, status
from rest_framework.decorators import (api_view, authentication_classes,
                                       permission_classes)
from rest_framework.response import Response
from rest_framework.views import APIView

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
class Venues(generics.ListCreateAPIView):
    http_method_names = ['get']
    serializer_class = VenueSerializer

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        pk = self.request.query_params.get('id', None)
        q = Q()
        if name is not None:
            q.add(Q(name__icontains=name), Q.AND)

        if pk is not None:
            q.add(Q(location=pk), Q.AND)

        return Venue.objects.filter(q)


@authentication_classes([])
@permission_classes([])
class VenueEvents(APIView):
    http_method_names = ['get']

    def get(self, request, venue_id):
        start_str = self.request.query_params.get('start', None)
        end_str = self.request.query_params.get('end', None)

        if start_str is None or end_str is None:
            raise exceptions.NotFound(
                detail=_('start or end parameter not set'))

        try:
            start = dateutil.parser.parse(start_str).replace(tzinfo=None)
            end = dateutil.parser.parse(end_str).replace(tzinfo=None)
        except ValueError as e:
            raise exceptions.ParseError(
                detail=_('start or end parameter not valid iso_8601 string'))

        try:
            Venue.objects.get(id=venue_id)
        except Venue.DoesNotExist:
            raise exceptions.NotFound(
                detail=_('No venue corresponds to the given id'))

        events = Event.objects.filter(venue=venue_id)
        result = []

        for e in events:
            print(e.dtstart)
            occurrences = e.recurrences.between(
                start,
                end,
                inc=True,
                dtstart=e.dtstart.replace(tzinfo=None)
            )
            for o in occurrences:
                result.append({
                    'id': e.id,
                    'title': e.name,
                    'description': e.description,
                    'start': datetime.combine(o.date(), e.dtstart.time()),
                    'end': datetime.combine(o.date(), e.dtend.time()),
                })

        return Response(result)
