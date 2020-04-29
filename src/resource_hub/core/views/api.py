from django.db.models import Q

from resource_hub.core.models import Contract, Location, Notification, User
from resource_hub.core.serializers import (ActorSerializer, ContractSerializer,
                                           LocationSerializer,
                                           NotificationSerializer,
                                           UserSerializer)
from rest_framework import filters, generics
from rest_framework.decorators import (authentication_classes,
                                       permission_classes)
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from ..utils import get_authorized_actors


class SmallResultsSetPagination(PageNumberPagination):
    page_size = 9
    page_size_query_param = 'page_size'
    max_page_size = 1000


class NotificationResultsSetPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 1000


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
        return get_authorized_actors(self.request.user)


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


class ContractsList(generics.ListCreateAPIView):
    http_method_names = ['get']
    serializer_class = ContractSerializer
    pagination_class = SmallResultsSetPagination

    def get_queryset(self):
        contract_type = self.request.query_params.get('type', None)
        if contract_type is None:
            raise ValidationError('type argument is not set')

        if contract_type == 'creditor':
            query = Q(creditor=self.request.actor)
        elif contract_type == 'debitor':
            query = Q(debitor=self.request.actor)
        else:
            raise ValidationError('invalid type argument')

        return Contract.objects.filter(query).select_subclasses().order_by('-created_at')


class NotificationsList(generics.ListCreateAPIView):
    http_method_name = ['get']
    serializer_class = NotificationSerializer
    pagination_class = NotificationResultsSetPagination

    def get_queryset(self):
        actor = self.request.actor
        return Notification.objects.filter(recipient=actor).order_by('-created_at')


class NotificationsUnread(APIView):
    def get(self, request):
        actor = request.actor
        data = {
            'count': Notification.objects.filter(is_read=False, recipient=actor).count(),
        }
        return Response(data)


class NotificationsMarkRead(APIView):
    def put(self, request):
        pk = request.POST.get('pk')
        actor = request.actor
        query = Q(pk=pk, recipient=actor) if pk else Q(recipient=actor)
        Notification.objects.filter(query).update(is_read=True)
        return Response({'detail': 'updated notification status as read'})
