from datetime import datetime

import dateutil.parser
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from resource_hub.core.views.api import SmallResultsSetPagination
from resource_hub.workshops.models import Workshop, WorkshopBooking
from resource_hub.workshops.serializers import WorkshopSerializer
from rest_framework import exceptions, generics
from rest_framework.decorators import (authentication_classes,
                                       permission_classes)
from rest_framework.response import Response
from rest_framework.views import APIView


@authentication_classes([])
@permission_classes([])
class Workshops(generics.ListCreateAPIView):
    http_method_names = ['get']
    serializer_class = WorkshopSerializer
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        pk = self.request.query_params.get('id', None)
        q = Q()
        if name is not None:
            q.add(Q(name__icontains=name), Q.AND)

        if pk is not None:
            q.add(Q(location=pk), Q.AND)

        return Workshop.objects.filter(q)


@authentication_classes([])
@permission_classes([])
class WorkshopEvents(APIView):
    http_method_names = ['get']

    def get(self, request, pk):
        start_str = self.request.query_params.get('start', None)
        end_str = self.request.query_params.get('end', None)

        if start_str is None or end_str is None:
            raise exceptions.NotFound(
                detail=_('start or end parameter not set'))

        try:
            start = dateutil.parser.parse(start_str)
            end = dateutil.parser.parse(end_str)
        except ValueError as e:
            raise exceptions.ParseError(
                detail=_('start or end parameter not valid iso_8601 string'))

        try:
            Workshop.objects.get(pk=pk)
        except Workshop.DoesNotExist:
            raise exceptions.NotFound(
                detail=_('No workshop corresponds to the given id'))

        events = WorkshopBooking.objects.filter(workshops=pk, is_deleted=False)
        result = []

        for e in events:
            occurrences = e.recurrences.between(
                start,
                end,
                inc=True,
                dtstart=e.dtstart
            )
            for o in occurrences:
                result.append({
                    'id': e.id,
                    'title': _('Workplaces: %(workplaces)d') % {'workplaces': e.workplaces, },
                    'start': datetime.combine(o.date(), e.dtstart.time(), e.dtstart.tzinfo),
                    'end': datetime.combine(o.date(), e.dtend.time(), e.dtend.tzinfo),
                })

        return Response(result)
