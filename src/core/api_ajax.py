from rest_framework import status, filters, generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from core.models import User, Organization, OrganizationMember
from core.serializers import UserSerializer


class UserSearch(generics.ListCreateAPIView):
    http_method_names = ['get']
    search_fields = ['username', 'first_name', 'last_name']
    filter_backends = (filters.SearchFilter,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRoles(APIView):
    def get(self, request, format=None):
        user = request.user
        organizations = Organization.objects.filter(
            organizationmember__user=user, organizationmember__role=OrganizationMember.ADMIN)
        return Response(organizations.values())


class OrganizationMemberChangeRole(APIView):
    def post(self, request, format=None):
        data = request.POST
        print(data)
        return Response(data)
