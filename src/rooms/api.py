from django.forms.models import model_to_dict

from rest_framework import status, filters, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.models import Room, Event
from rooms.serializers import RoomSerializer


# class UserSearch(generics.ListCreateAPIView):
#     http_method_names = ['get']
#     search_fields = ['username', 'first_name', 'last_name']
#     filter_backends = (filters.SearchFilter,)
#     queryset = User.objects.all()
#     serializer_class = UserSerializer

class Rooms(generics.ListCreateAPIView):
    http_method_names = ['get']
    search_fields = ['name']
    filter_backends = (filters.SearchFilter,)
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
