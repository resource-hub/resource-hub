from django.test import TestCase
from django.contrib.auth.models import User
from core.models import *
from django.utils.dateparse import parse_date


class TestUser(TestCase):
    @classmethod
    def setUpTestData(cls):
        address = Address.objects.create(
            street='Test Street',
            street_number='12A',
            postal_code='12345',
            city='Test City',
        )
        bank_account = BankAccount.objects.create(
            account_holder='Test Face',
            iban='DE12500105170648489890',
            bic='INGDDEFFXXX',
        )
        info = Info.objects.create(
            address=address,
            bank_account=bank_account,
            website='https://test.de'
        )
        user = User.objects.create(
            first_name='Test',
            last_name='Face',
            username='testmate',
            birth_date=parse_date('2018-01-01'),
            info=info,
        )

    def test_person_first_name(self):
        user = User.objects.get(username='testmate')
        first_name = user.first_name
        self.assertEqual('Test', first_name)
