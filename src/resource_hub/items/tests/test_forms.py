import base64
from datetime import datetime, timezone

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.timezone import get_current_timezone

from recurrence.models import Recurrence
from resource_hub.core.models import Actor, Address, Location, PaymentMethod

from ..forms import ItemForm
from ..models import ItemContractProcedure

TEST_IMAGE = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQYV2NgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII='


class TestEventForm(TestCase):
    def setUp(self):
        self.actor = Actor.objects.create(
            name='Test Joe'
        )
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
            address=address,
            latitude=53.00,
            longitude=9.0,
            owner=actor
        )
        self.payment_method = PaymentMethod.objects.create(
            currency='EUR',
            owner=self.actor,
        )
        self.contract_procedure = ItemContractProcedure.objects.create(
            name='test',
            owner=self.actor,
        )

    def get_data(self):
        return {
            'name': 'item',
            'description': 'test',

            'owner': self.actor.pk,
            'location': self.location.pk,

        }

    def get_media(self):
        return {
            'thumbnail_original': SimpleUploadedFile(
                'default.png',
                base64.b64decode(TEST_IMAGE),
                content_type='image/png'
            )
        }
