from rest_framework import status, filters, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from core.models import User
from core.serializers import UserSerializer


class UserSearch(generics.ListCreateAPIView):
    http_method_names = ['get']
    search_fields = ['username']
    filter_backends = (filters.SearchFilter,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
