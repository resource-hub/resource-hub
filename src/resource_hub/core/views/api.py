from django.db.models import Q

from resource_hub.core.models import (Actor, Contract, Location,
                                      OrganizationMember, User)
from resource_hub.core.serializers import (ActorSerializer, ContractSerializer,
                                           LocationSerializer, UserSerializer)
from resource_hub.core.utils import get_associated_objects
from rest_framework import filters, generics
from rest_framework.decorators import (authentication_classes,
                                       permission_classes)
from rest_framework.response import Response
from rest_framework.views import APIView


class UserSearch(generics.ListCreateAPIView):
    http_method_names = ['get']
    search_fields = ['username', 'first_name', 'last_name']
    filter_backends = (filters.SearchFilter,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ActorList(generics.ListCreateAPIView):
    http_method_names = ['get']
    serializer_class = ActorSerializer

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
class Locations(generics.ListCreateAPIView):
    http_method_names = ['get']
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class Contracts(generics.ListCreateAPIView):
    http_method_names = ['get']
    serializer_class = ContractSerializer

    def get_queryset(self):
        return Contract.objects.filter(Q(creditor=self.request.actor) | Q(debitor=self.request.actor)).select_subclasses()
