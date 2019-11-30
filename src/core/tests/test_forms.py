from datetime import datetime, timedelta
import os

from django.forms import ValidationError
from django.http.request import HttpRequest
from django.test import TestCase

from core.forms import *

DATA = {
    "first_name": "Test",
    "last_name": "Face",
    "username": "test",
    "email": "test@ture.dev",
    "old_email": "test@ture.dev",
    "new_email1": "test@mail.de",
    "new_email2": "test@mail.de",
    "password": "we8dlz49opd",
    "password1": "we8dlz49opd",
    "password2": "we8dlz49opd",
    "birth_date": "1997-01-01",
    "telephone_private": "123092813124",
    "telephone_public": "00000000000",
    "email_public": "test@mail.de",
    "website": "https://test.de",
    "info_text": "<h1>hello!</h1>",
    "account_holder": "Test Face",
    "iban": "DE12500105170648489890",
    "bic": "INGDDEFFXXX",
    "street": "Test Street",
    "street_number": "12A",
    "postal_code": "12345",
    "city": "Test City",
    "country": "Germany"

}


class TestUserBaseForm(TestCase):
    def setUp(self):
        self.data = DATA.copy()

    def test_valid_data(self):
        form = UserBaseForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_invalid_birth_data(self):
        invalid_data = self.data.copy()
        invalid_data['birth_date'] = '1880-01-01'
        form = UserBaseForm(data=invalid_data)
        self.assertFalse(form.is_valid())

        MINIMUM_AGE_IN_YEARS = 7
        below_minimum_age = MINIMUM_AGE_IN_YEARS*365-1
        birth_date = datetime.today() - timedelta(days=below_minimum_age)
        invalid_data['birth_date'] = birth_date.date().isoformat()
        form = UserBaseForm(data=invalid_data)
        self.assertFalse(form.is_valid())


class TestBankAccountForm(TestCase):
    def setUp(self):
        self.data = DATA.copy()
        self.path = os.path.dirname(os.path.abspath(__file__))

    def test_valid_data(self):
        with open(os.path.join(self.path, '_valid_iban.txt')) as f:
            for iban in f:
                self.data['iban'] = iban
                form = BankAccountForm(data=self.data)
                self.assertTrue(form.is_valid())

    def test_invalid_data(self):
        invalid_data = self.data.copy()
        with open(os.path.join(self.path, '_invalid_iban.txt')) as f:
            for iban in f:
                invalid_data['iban'] = iban
                form = BankAccountForm(data=invalid_data)
                self.assertFalse(form.is_valid())


class TestInfoFormManager(TestCase):
    def setUp(self):
        self.data = DATA.copy()

    def test_empty_form(self):
        forms = InfoFormManager().get_forms()
        self.assertTrue('info_form' in forms)
        self.assertTrue('address_form' in forms)
        self.assertTrue('bank_account_form' in forms)

    def test_valid_data(self):
        request = HttpRequest()
        request.POST = self.data
        info_form = InfoFormManager(request)
        self.assertTrue(info_form.is_valid())

        new_info = info_form.save()
        info = Info.objects.get(pk=1)
        self.assertEqual(new_info, info)


class TestEmailChangeForm(TestCase):
    def setUp(self):
        self.data = DATA.copy()
        self.user = User.objects.create_user(
            username=self.data['username'],
            email=self.data['old_email'],
            password=self.data['password'],
            birth_date=self.data['birth_date'],
        )

    def test_valid_data(self):
        form = EmailChangeForm(self.user, self.data)
        self.assertTrue(form.is_valid())

    def test_wrong_password(self):
        invalid_data = self.data.copy()
        invalid_data['password'] = 'x'
        form = EmailChangeForm(self.user, invalid_data)
        self.assertFalse(form.is_valid())

    def test_non_matching_email(self):
        invalid_data = self.data.copy()
        invalid_data['new_email1'] = 'test@test.de'
        form = EmailChangeForm(self.user, invalid_data)
        self.assertFalse(form.is_valid())

        invalid_data = self.data.copy()
        invalid_data['new_email2'] = 'test@test.de'
        form = EmailChangeForm(self.user, invalid_data)
        self.assertFalse(form.is_valid())
