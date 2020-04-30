from django.shortcuts import reverse
from django.test import TestCase

from rest_framework.test import (APIClient, APIRequestFactory,
                                 force_authenticate)
from rest_framework.views import APIView

from ..models import Organization, OrganizationMember, User
from ..views.api import OrganizationMembersChange

USER_DATA = {
    'name': 'test',
    'username': 'test',
    'email': 'test@test.de',
}


class BaseAPITest(TestCase):
    COUNT = 0

    def setUp(self):
        self.client = APIClient()
        self.url = ''
        self.view = APIView
        self.user1 = self.create_user()
        self.user2 = self.create_user()
        self.factory = APIRequestFactory()

    def create_user(self):
        user = User.objects.create(**USER_DATA)
        self.COUNT += 1
        USER_DATA['email'] = USER_DATA['email'] + str(self.COUNT)
        USER_DATA['username'] = str(self.COUNT) + USER_DATA['username']
        USER_DATA['name'] = USER_DATA['name'] + str(self.COUNT)
        return user

    def post(self, data, user, kwargs=None):
        request = self.factory.post(self.url, data, format='json')
        force_authenticate(request, user=user)
        response = self.view(request, **kwargs)
        self.assertEqual(response.status_code, 200)
        return response


class TestOrganizationMembersChange(BaseAPITest):
    def setUp(self):
        super(TestOrganizationMembersChange, self).setUp()
        self.organization = Organization.objects.create(
            name='test'
        )
        self.url = reverse('api:organizations_members_change', kwargs={
                           'organization_pk': self.organization.pk})
        self.view = OrganizationMembersChange.as_view()
        self.organization.members.add(self.user1, through_defaults={
            'role': OrganizationMember.OWNER})
        self.organization.members.add(self.user2, through_defaults={
            'role': OrganizationMember.MEMBER})

    def test_change(self):
        m = OrganizationMember.objects.get(
            user=self.user2,
            organization=self.organization
        )
        self.post({
            m.pk: {
                'role': OrganizationMember.ADMIN
            },
        }, self.user1, kwargs={'organization_pk': self.organization.pk})
        self.assertEqual(OrganizationMember.objects.get(
            organization=self.organization,
            user=self.user2,
        ).role, OrganizationMember.ADMIN)
