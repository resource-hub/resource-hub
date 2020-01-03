from django.db.models import Q
from django.forms.models import model_to_dict

from rest_framework import status, filters, generics
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User, Actor, Location, OrganizationMember
from core.serializers import UserSerializer, ActorSerializerMinimal, LocationSerializer


class UserSearch(generics.ListCreateAPIView):
    http_method_names = ['get']
    search_fields = ['username', 'first_name', 'last_name']
    filter_backends = (filters.SearchFilter,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ActorList(generics.ListCreateAPIView):
    http_method_names = ['get']
    serializer_class = ActorSerializerMinimal

    def get_queryset(self):
        user = self.request.user
        query = Q(pk=user.pk)
        sub_condition = Q(organization__members=user)
        sub_condition.add(
            Q(organization__organizationmember__role__gte=OrganizationMember.ADMIN), Q.AND)
        query.add(sub_condition, Q.OR)
        return Actor.objects.filter(query)


class ActorChange(APIView):
    def post(self, request, format=None):
        data = request.POST
        return Response(data)


@authentication_classes([])
@permission_classes([])
class LocationFeed(generics.ListCreateAPIView):
    http_method_names = ['get']
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
