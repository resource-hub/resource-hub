import base64
from datetime import datetime, timezone

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.timezone import get_current_timezone
from recurrence.models import Recurrence
from resource_hub.core.models import Actor, Address, Location, PaymentMethod
from resource_hub.core.tests import LoginTestMixin

from ..forms import ItemFormManager
from ..models import Item, ItemContractProcedure

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
        self.actor = self.user

    def get_data(self):
        return {
            'name': 'item',
            'description': 'test',
            'contract_procedure': self.contract_procedure,
            'unit': Item.UNIT.DAYS,
            'maximum_duration': 0,
            'self_pickup': Item.SELF_PICKUP.NOT_ALLOWED,
            'category': Item.CATEGORY.OTHER,
            'owner': self.user.pk,
            'location': self.location.pk,
            'images-TOTAL_FORMS': 0,
            'images-INITIAL_FORMS': 0,
            'prices-TOTAL_FORMS': 0,
            'prices-INITIAL_FORMS': 1,
            'prices-MIN_NUM_FORMS': 1,
            'prices-MAX_NUM_FORMS': 1000,
            'prices-0-price_ptr': None,
            'prices-0-item': None,
            'prices-0-addressee': None,
            'prices-0-value': 10,
            'prices-0-currency': 'EUR',
            'prices-0-discounts': 'on',
            'prices-0-ORDER': 0,
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
        form = ItemFormManager(
            self.user,
            self.actor,
            data=self.get_data(),
            files=self.get_files(),
        )
        self.assertTrue(form.is_valid())
        self.assertIsNotNone(form.save())
