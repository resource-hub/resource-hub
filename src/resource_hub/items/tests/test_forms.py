import base64
from datetime import datetime, timezone

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.timezone import get_current_timezone

from recurrence.models import Recurrence
from resource_hub.core.models import Actor, Address, Location, PaymentMethod
from resource_hub.core.tests import LoginTestMixin

from ..forms import ItemForm
from ..models import ItemContractProcedure

TEST_IMAGE = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQYV2NgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII='


class TestItemForm(LoginTestMixin, TestCase):
    def setUp(self):
        super(TestItemForm, self).setUp()
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
            owner=self.user
        )
        self.payment_method = PaymentMethod.objects.create(
            currency='EUR',
            owner=self.user,
        )
        self.contract_procedure = ItemContractProcedure.objects.create(
            name='test',
            owner=self.user,
        )
        self.request = self.client.get('')

    def get_data(self):
        return {
            'name': 'item',
            'description': 'test',
            'contract_procedure': self.contract_procedure,
            'owner': self.actor.pk,
            'location': self.location.pk,
            'prices-TOTAL_FORMS': 1,
            'prices-INTIAL_FORMS': 0,
            'prices-0-value': 10,
            'prices-0-currency': 'EUR',
            'prices-0-discounts': 'on',
        }

    def get_files(self):
        return {
            'thumbnail_original': SimpleUploadedFile(
                'default.png',
                base64.b64decode(TEST_IMAGE),
                content_type='image/png'
            )
        }

    def test_valid_data(self):
        form = ItemForm(
            self.request,
            data=self.get_data(),
            files=self.get_files(),
        )
        self.assertTrue(form.is_valid())
