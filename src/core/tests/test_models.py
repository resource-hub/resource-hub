from django.test import TestCase
from django.contrib.auth.models import User
from django.utils.dateparse import parse_date

from core.models import *
from . import create_test_users


class TestUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        create_test_users()

    def test_person_first_name(self):
        user = User.objects.get(username='testmate')
        first_name = user.first_name
        self.assertEqual('Test', first_name)
