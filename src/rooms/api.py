from django.forms.models import model_to_dict

from rest_framework import status, filters, generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.models import Room, Event
from rooms.serializers import RoomSerializer


@authentication_classes([])
@permission_classes([])
class Rooms(generics.ListCreateAPIView):
    http_method_names = ['get']
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
