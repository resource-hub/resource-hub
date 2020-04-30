from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from resource_hub.core.models import *
from resource_hub.core.tokens import TokenGenerator

USER_DATA = {
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
    'account_holder': 'Peter Popper',
    'iban': 'DE12500105170648489890',
    'bic': 'INGDDEFFXXX',
    'telephone_public': '+49123412341234',
    'telephone_private': '+49123412341234',
    'email_public': 'test@ture.dev',
    'website': 'https://wasmitherz.de',
    'info_text': 'Hello this is me.',
}


class TestView():
    view_name = 'empty'
    kwargs = None

    def setUp(self):
        self.client = Client()
        self.user = self.register_test_user()

    def register_test_user(self):
        response = self.client.post(
            reverse('core:register'), USER_DATA)

        user = User.objects.get(username=USER_DATA['username'])
        user.is_active = True
        user.save()
        self.client.login(
            username=USER_DATA['username'], password=USER_DATA['password'])
        return user

    def test_status_code(self):
        response = self.client.get(reverse(self.view_name, kwargs=self.kwargs))
        self.assertEqual(response.status_code, 200)


class TestHome(TestView, TestCase):
    view_name = 'core:home'


class TestSupport(TestView, TestCase):
    view_name = 'core:report_bug'


class TestLanguage(TestView, TestCase):
    view_name = 'core:language'


class TestRegistration(TestView, TestCase):
    view_name = 'core:register'

    def setUp(self):
        self.client = Client()
        self.USER_data = USER_DATA.copy()

    def test_created_user(self):
        response = self.client.post(
            reverse('core:register'), self.USER_data)
        user = User.objects.get(username=self.USER_data['username'])
        self.assertEqual(user.first_name, self.USER_data['first_name'])

    def test_created_info(self):
        response = self.client.post(
            reverse('core:register'), self.USER_data)
        user = Actor.objects.get(user__username=self.USER_data['username'])
        self.assertEqual(user.info_text, self.USER_data['info_text'])

    def test_post_status_code(self):
        response = self.client.post(
            reverse('core:register'), self.USER_data)
        self.assertEqual(response.status_code, 302)


class TestActivate(TestView, TestCase):
    view_name = 'core:verify'

    def test_status_code(self):
        response = self.client.get(reverse(self.view_name, kwargs={
            'uidb64': urlsafe_base64_encode(force_bytes(self.user.pk)),
            'token': TokenGenerator().make_token(self.user),
        }))
        self.assertEqual(response.status_code, 302)


class TestCustomLogin(TestCase):
    def setUp(self):
        self.client = Client()

    def test_status_code(self):
        response = self.client.get(reverse('core:login'))
        self.assertEqual(response.status_code, 200)


class TestSetRole(TestView, TestCase):
    view_name = 'core:actor_set'

    def test_status_code(self):
        response = self.client.post(reverse(self.view_name))
        self.assertEqual(response.status_code, 302)


class TestAdmin(TestView, TestCase):
    view_name = 'control:home'


class TestAccountSecurity(TestView, TestCase):
    def test_status_code(self):
        scope = ['email', 'password', ]

        for s in scope:
            response = self.client.get(
                reverse('control:account_security', kwargs={'scope': s}))
            self.assertEqual(response.status_code, 200)


class TestAccountSettings(TestView, TestCase):
    def test_status_code(self):
        scope = ['info', 'address', 'bank_account', ]

        for s in scope:
            response = self.client.get(
                reverse('control:account_settings', kwargs={'scope': s}))
            self.assertEqual(response.status_code, 200)


class TestOrganizationsManage(TestView, TestCase):
    view_name = 'control:organizations_manage'


class TestOrganizationsCreate(TestView, TestCase):
    view_name = 'control:organizations_create'
