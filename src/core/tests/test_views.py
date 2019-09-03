from django.test import TestCase, Client
from django.urls import reverse
from core.models import *


class TestRegistration(TestCase):
    def setUp(self):
        self.client = Client()
        self.post_body = {
            'username': 'peterpopper',
            'email': 'test@ture.dev',
            'password1': 'we8dlz49opd',
            'password2': 'we8dlz49opd',
            'first_name': 'Peter',
            'last_name': 'Popper',
            'birth_date': '05/31/1997',
            'street': 'Test Str.',
            'street_number': '12',
            'postal_code': '12345',
            'city': 'Hannover',
            'country': 'Germany',
            'account_holder': 'Peter Popper',
            'iban': 'DE12500105170648489890',
            'bic': 'INGDDEFFXXX',
            'telephone_public': '+49123412341234',
            'telephone_private': '+49123412341234',
            'email_public': 'test@ture.dev',
            'website': 'https://wasmitherz.de',
            'info_text': 'Hello this is me.',
        }

        self.response = self.client.post(
            reverse('core:register'), self.post_body)

    def test_registration_status_code(self):
        self.assertEqual(self.response.status_code, 302)

    def test_created_user(self):
        user = User.objects.get(username=self.post_body['username'])
        self.assertEqual(self.post_body['first_name'], user.first_name)

    def test_created_info(self):
        id = user = User.objects.get(username=self.post_body['username']).id
        person = Person.objects.select_related().get(user=id)
        self.assertEqual(person.info.info_text, self.post_body['info_text'])
