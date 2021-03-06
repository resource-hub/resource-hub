from unittest import SkipTest

from django.test import TestCase

from ..models import Address, ContractProcedure, Location, Organization, User
from .test_views import LoginTestMixin


class BaseTest(TestCase):
    view_name = 'empty'
    kwargs = None

    def setUp(self):
        if self.__class__ == BaseTest:
            raise SkipTest('Abstract test')
        super(BaseTest, self).setUp()
        self.user = User.objects.create(
            username='Joe',
            email='joe@joe.de',
            name='Joe McJoe',
        )
        self.organization = Organization.objects.create(
            name='Org',
        )
        self.address = Address.objects.create(
            street='street',
            street_number=12,
            postal_code='12345',
            city='test',
            country='de'
        )
        self.location = Location.objects.create(
            name='Location',
            description='nice',
            address=self.address,
            latitude=53.00,
            longitude=9.0,
            owner=self.user,
        )
        self.contract_procedure = ContractProcedure.objects.create(
            owner=self.user,
        )
