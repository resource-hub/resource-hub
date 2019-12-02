from django.contrib.auth import login
from django.forms.models import model_to_dict
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_text

from core.models import *
from core.tokens import TokenGenerator

DATA = {
    'username': 'peterpopper',
    'email': 'test@ture.dev',
    'password': 'we8dlz49opd',
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


def register_test_user(client):
    response = client.post(
        reverse('core:register'), DATA)

    user = User.objects.get(username=DATA['username'])
    user.is_active = True
    user.save()
    client.login(username=DATA['username'], password=DATA['password'])
    return user


class TestHome(TestCase):
    def setUp(self):
        self.client = Client()

    def test_status_code(self):
        response = self.client.get(reverse('core:home'))
        self.assertEqual(response.status_code, 200)


class TestSupport(TestCase):
    def setUp(self):
        self.client = Client()

    def test_status_code(self):
        response = self.client.get(reverse('core:support'))
        self.assertEqual(response.status_code, 200)


class TestLanguage(TestCase):
    def setUp(self):
        self.client = Client()

    def test_status_code(self):
        response = self.client.get(reverse('core:language'))
        self.assertEqual(response.status_code, 200)


class TestRegistration(TestCase):
    def setUp(self):
        self.data = DATA.copy()
        self.client = Client()

    def test_created_user(self):
        response = self.client.post(
            reverse('core:register'), self.data)
        user = User.objects.get(username=self.data['username'])
        self.assertEqual(user.first_name, self.data['first_name'])

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


class TestActivate(TestCase):
    def setUp(self):
        self.client = Client()

    def test_status_code(self):
        user = register_test_user(self.client)
        response = self.client.get(reverse('core:activate', kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(user.pk)),
            'token': TokenGenerator().make_token(user),
        }))
        self.assertEqual(response.status_code, 302)


class TestCustomLogin(TestCase):
    def setUp(self):
        self.client = Client()

    def test_status_code(self):
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)


class TestSetRole(TestCase):
    def setUp(self):
        self.client = Client()
        register_test_user(self.client)

    def test_status_code(self):
        response = self.client.post(reverse('core:set_role'))
        self.assertEqual(response.status_code, 302)


class TestAdmin(TestCase):
    def setUp(self):
        self.client = Client()
        register_test_user(self.client)

    def test_status_code(self):
        response = self.client.get(reverse('core:admin'))
        self.assertEqual(response.status_code, 200)


class TestAccountSettings(TestCase):
    def setUp(self):
        self.client = Client()
        register_test_user(self.client)

    def test_status_code(self):
        scope = ['email', 'password', ]

        for s in scope:
            response = self.client.get(
                reverse('core:account_settings', kwargs={'scope': s}))
            self.assertEqual(response.status_code, 200)


class TestAccountProfile(TestCase):
    def setUp(self):
        self.client = Client()
        register_test_user(self.client)

    def test_status_code(self):
        scope = ['info', 'address', 'bank_account', ]

        for s in scope:
            response = self.client.get(
                reverse('core:account_profile', kwargs={'scope': s}))
            self.assertEqual(response.status_code, 200)


class TestOrganizationsManage(TestCase):
    def setUp(self):
        self.client = Client()
        register_test_user(self.client)

    def test_status_code(self):
        response = self.client.get(reverse('core:organizations_manage'))
        self.assertEqual(response.status_code, 200)


class TestOrganizationCreate(TestCase):
    def setUp(self):
        self.client = Client()
        register_test_user(self.client)

    def test_status_code(self):
        response = self.client.get(reverse('core:organizations_create'))
        self.assertEqual(response.status_code, 200)
