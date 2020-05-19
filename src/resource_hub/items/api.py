from datetime import datetime

import dateutil.parser
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from resource_hub.core.views.api import SmallResultsSetPagination
from rest_framework import exceptions, generics
from rest_framework.decorators import (authentication_classes,
                                       permission_classes)
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Item
from .serializers import ItemSerializer


@authentication_classes([])
@permission_classes([])
class Items(generics.ListCreateAPIView):
    http_method_names = ['get']
    serializer_class = ItemSerializer
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        name = self.request.query_params.get('name', None)
        pk = self.request.query_params.get('id', None)
        q = Q()
        if name is not None:
            q.add(Q(name__icontains=name), Q.AND)

        if pk is not None:
            q.add(Q(location=pk), Q.AND)

        return Item.objects.filter(q)
