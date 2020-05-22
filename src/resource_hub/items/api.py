from datetime import datetime

from django.db.models import F, Q
from django.utils.translation import gettext_lazy as _

import dateutil.parser
from resource_hub.core.models import Contract
from resource_hub.core.views.api import SmallResultsSetPagination
from rest_framework import exceptions, generics
from rest_framework.decorators import (authentication_classes,
                                       permission_classes)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Item, ItemBooking
from .serializers import ItemBookingSerializer, ItemSerializer


@authentication_classes([])
@permission_classes([])
class Items(generics.ListCreateAPIView):
    http_method_names = ['get']
    serializer_class = ItemSerializer
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        pk = self.request.query_params.get('id', None)
        q = Q(state=Item.STATE.AVAILABLE)
        if name is not None:
            q.add(Q(name__icontains=name), Q.AND)

        if pk is not None:
            q.add(Q(location=pk), Q.AND)
        return Item.objects.filter(q)


@authentication_classes([])
@permission_classes([])
class Bookings(generics.ListCreateAPIView):
    http_method_names = ['get']
    serializer_class = ItemBookingSerializer
    lookup_url_kwarg = 'pk'

    def get_queryset(self):
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
        item = self.kwargs.get(self.lookup_url_kwarg)

        return ItemBooking.objects.filter(
            item=item,
            dtend__gt=start,
            dtstart__lt=end,
        )
