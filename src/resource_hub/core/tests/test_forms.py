import os
from datetime import datetime, timedelta

from django.forms import ValidationError
from django.http.request import HttpRequest
from django.test import TestCase

from resource_hub.core.forms import *
from resource_hub.core.tests import BaseTest

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
    "country": "de",
}


class TestUserBaseForm(TestCase):
    def setUp(self):
        self.data = DATA.copy()

    def test_valid_data(self):
        form = UserBaseForm(data=self.data)
        self.assertTrue(form.is_valid())

    def test_user_invitation(self):
        organization = Organization.objects.create(
            name='test',
        )
        invitee = User.objects.create(
            name='joe',
            email='test@test.de',
        )
        OrganizationInvitation.objects.create(
            invitee=invitee,
            organization=organization,
            email=self.data['email'],
            role=OrganizationMember.MEMBER,
        )
        form = UserBaseForm(data=self.data)
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertTrue(organization.members.get(pk=user.pk))

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


class TestOrganizationInvitationManagementForm(BaseTest):
    def setUp(self):
        super(TestOrganizationInvitationManagementForm, self).setUp()
        self.data = {
            'text': '<p>Testitest</p>',
            'invitations-TOTAL_FORMS': 1,
            'invitations-INITIAL_FORMS': 0,
            'invitations-MIN_NUM_FORMS': 0,
            'invitations-MAX_NUM_FORMS': 1000,
            'invitations-0-id': '',
            'invitations-0-organization': self.organization.pk,
            'invitations-0-email': self.user.email,
            'invitations-0-role': OrganizationMember.ADMIN,
        }

    def test_inviting_user(self):
        form = OrganizationInvitationFormManager(
            self.user, self.user, organization=self.organization, data=self.data)
        self.assertTrue(form.is_valid())
        form.save()
        invitation = OrganizationInvitation.objects.get(
            email=self.user.email, role=OrganizationMember.ADMIN)
        self.assertEqual(invitation.text, self.data['text'])
        self.assertTrue(invitation.is_member)
        self.assertTrue(self.organization.members.get(pk=self.user.pk))

    def test_inviting_non_user(self):
        invited_user = {
            'email': 'mac@mac.de',
            'role': OrganizationMember.MEMBER,
        }
        data = {
            **self.data,
            'invitations-TOTAL_FORMS': 2,
            'invitations-1-id': '',
            'invitations-1-organization': self.organization.pk,
            'invitations-1-email': invited_user['email'],
            'invitations-1-role': invited_user['role'],
        }
        form = OrganizationInvitationFormManager(
            self.user, self.user, organization=self.organization, data=data)

        self.assertTrue(form.is_valid())
        form.save()
        invitation = OrganizationInvitation.objects.get(
            email=invited_user['email'], role=invited_user['role'])
        self.assertEqual(invitation.text, data['text'])

    def test_inviting_member(self):
        self.organization.members.add(self.user, through_defaults={
            'role': OrganizationMember.ADMIN,
        })
        form = OrganizationInvitationFormManager(
            self.user, self.user, organization=self.organization, data=self.data)
        self.assertTrue(form.is_valid())
        form.save()
