from django.test import TestCase, Client
from django.urls import reverse
from core.models import *


class TestRegistration(TestCase):
    def setUp(self):
        self.client = Client()
        self.data = {
            'username': 'peterpopper',
            'email': 'test@ture.dev',
            'password1': 'we8dlz49opd',
            'password2': 'we8dlz49opd',
            'first_name': 'Peter',
            'last_name': 'Popper',
            'birth_date': '1997-05-31',
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

    def test_created_user(self):
        response = self.client.post(
            reverse('core:register'), self.data)
        user = User.objects.get(username=self.data['username'])
        self.assertEqual(self.data['first_name'], user.first_name)

    def test_created_info(self):
        response = self.client.post(
            reverse('core:register'), self.data)
        user = User.objects.get(username=self.data['username'])
        self.assertEqual(user.info.info_text, self.data['info_text'])

    def test_get_status_code(self):
        response = self.client.get(reverse('core:register'))
        self.assertEqual(response.status_code, 200)

    def test_post_status_code(self):
        response = self.client.post(
            reverse('core:register'), self.data)
        self.assertEqual(response.status_code, 302)
