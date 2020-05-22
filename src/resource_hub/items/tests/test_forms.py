import base64
from datetime import datetime, timedelta, timezone

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils import timezone
from django.utils.timezone import get_current_timezone

from recurrence.models import Recurrence
from resource_hub.core.models import Actor, Address, Location, PaymentMethod
from resource_hub.core.tests import LoginTestMixin

from ..forms import ItemBookingForm, ItemFormManager
from ..models import Item, ItemBooking, ItemContract, ItemContractProcedure

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
            'state': Item.STATE.AVAILABLE,
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


class TestItemBookingForm(LoginTestMixin, TestCase):
    def setUp(self):
        super(TestItemBookingForm, self).setUp()
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
        self.item = Item.objects.create(
            name='test',
            state=Item.STATE.AVAILABLE,
            description='test',
            location=self.location,
            quantity=1,
            unit=Item.UNIT.HOURS,
            contract_procedure=self.contract_procedure,
            maximum_duration=7,
            owner=self.actor,
        )
        self.contract = ItemContract.objects.create(

        )
        self.item_booking = ItemBooking.objects.create(
            item=self.item,
            contract=self.contract,
            dtstart=datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            dtend=datetime(2020, 1, 1, 14, 0, 0, tzinfo=timezone.utc),
            quantity=1,
        )

    def _test_bookings(self, bookings, bool_):
        for booking in bookings:
            form = ItemBookingForm(
                self.item,
                data=booking,
            )
            self.assertEqual(form.is_valid(), bool_)

    def test_conflicting_bookings_hours(self):
        bookings = [
            # start inside
            {
                'dtstart': datetime(2020, 1, 1, 12, 30, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 1, 14, 30, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
            # booking within
            {
                'dtstart': datetime(2020, 1, 1, 13, 30, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 1, 14, 0, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
            # booking complete overshadowing
            {
                'dtstart': datetime(2020, 1, 1, 11, 0, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 1, 16, 0, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
            # booking equal
            {
                'dtstart': datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 1, 14, 0, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
        ]
        self._test_bookings(bookings, False)

    def test_valid_bookings_hours(self):
        bookings = [
            # booking completely outside
            {
                'dtstart': datetime(2020, 1, 1, 11, 0, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 1, 11, 30, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
            # booking end equal
            {
                'dtstart': datetime(2020, 1, 1, 11, 30, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
            # booking start equal
            {
                'dtstart': datetime(2020, 1, 1, 14, 0, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 1, 15, 0, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
        ]
        self._test_bookings(bookings, True)

    def test_conflicting_bookings_days(self):
        self.item_booking.unit = Item.UNIT.DAYS
        self.item_booking.dtend = datetime(
            2020, 1, 3, 15, 0, 0, tzinfo=timezone.utc)
        self.item_booking.save()

        bookings = [
            # start inside
            {
                'dtstart': datetime(2020, 1, 2, 12, 30, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 4, 14, 30, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
            # booking within
            {
                'dtstart': datetime(2020, 1, 2, 13, 30, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 2, 14, 0, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
            # booking complete overshadowing
            {
                'dtstart': datetime(2019, 12, 31, 11, 0, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 4, 16, 0, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
            # booking equal
            {
                'dtstart': datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 3, 14, 0, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
        ]
        self._test_bookings(bookings, False)

    def test_valid_bookings_days(self):
        self.item_booking.item.unit = Item.UNIT.DAYS
        self.item_booking.dtend = datetime(
            2020, 1, 3, 15, 0, 0, tzinfo=timezone.utc)
        self.item_booking.save()
        bookings = [
            # booking completely outside
            {
                'dtstart': datetime(2020, 1, 4, 11, 0, 0, tzinfo=timezone.utc),
                'dtend': datetime(2020, 1, 5, 11, 30, 0, tzinfo=timezone.utc),
                'quantity': 1
            },
        ]
        self._test_bookings(bookings, True)

    def test_maximum_duration_hours(self):
        dtstart = datetime(2020, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
        dtend = dtstart + timedelta(hours=self.item.maximum_duration + 1)
        bookings = [
            {
                'dtstart': dtstart,
                'dtend': dtend,
                'quantity': 1,
            }
        ]
        self._test_bookings(bookings, False)

    def test_maximum_duration_days(self):
        self.item_booking.item.unit = Item.UNIT.DAYS
        self.item_booking.dtend = datetime(
            2020, 1, 3, 15, 0, 0, tzinfo=timezone.utc)
        self.item_booking.save()
        dtstart = datetime(2020, 1, 2, 12, 0, 0, tzinfo=timezone.utc)
        dtend = dtstart + timedelta(days=self.item.maximum_duration + 1)
        bookings = [
            {
                'dtstart': dtstart,
                'dtend': dtend,
                'quantity': 1,
            }
        ]
        self._test_bookings(bookings, False)
