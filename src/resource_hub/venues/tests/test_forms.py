import base64
from datetime import datetime, timezone

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.utils.timezone import get_current_timezone

from recurrence.models import Recurrence
from resource_hub.core.models import Actor, Address, Location

from ..forms import EventForm
from ..models import Event, Venue

TEST_IMAGE = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVQYV2NgYAAAAAMAAWgmWQ0AAAAASUVORK5CYII='


class TestEventForm(TestCase):
    def setUp(self):
        actor = Actor.objects.create(
            name='Test Joe'
        )
        address = Address.objects.create(
            street='street',
            street_number=12,
            postal_code='12345',
            city='test',
            country='de'
        )
        location = Location.objects.create(
            name='Location',
            description='nice',
            address=address,
            latitude=53.00,
            longitude=9.0,
            owner=actor
        )
        self.venue = Venue.objects.create(
            name='Venue',
            description='nice',
            location=location,
            owner=actor,
        )

        Event.objects.create(
            name='event',
            description='1',
            dtstart=datetime(2020, 1, 1, 12, 0, 0,
                             tzinfo=timezone.utc),
            dtend=datetime(2020, 1, 1, 13, 0, 0,
                           tzinfo=timezone.utc),
            dtlast=datetime(2020, 1, 1, 13, 0, 0,
                            tzinfo=timezone.utc),
            organizer=actor,
            recurrences="DTSTART:20200101T120000Z\nRRULE:FREQ=WEEKLY;COUNT=5;"
        ).venues.add(self.venue)

        Event.objects.create(
            name='event',
            description='1',
            dtstart=datetime(2020, 1, 1, 13, 0, 0,
                             tzinfo=timezone.utc),
            dtend=datetime(2020, 1, 1, 14, 30, 0,
                           tzinfo=timezone.utc),
            dtlast=datetime(2020, 1, 1, 14, 30, 0,
                            tzinfo=timezone.utc),
            organizer=actor,
            recurrences="DTSTART:20200101T123000Z"
        ).venues.add(self.venue)

    def create_event_form(self, dtstart, dtend, recurrence, venue):
        return EventForm(
            venue,
            None,
            data={
                'venues': [venue.pk, ],
                'name': 'NewEvent',
                'description': 'test',
                'dtstart': dtstart,
                'dtend': dtend,
                'recurrences': recurrence,
            },
            files={
                'thumbnail_original': SimpleUploadedFile(
                    'default.png',
                    base64.b64decode(TEST_IMAGE),
                    content_type='image/png'
                )
            }
        )

    def test_conflicting_events(self):
        events = [
            # single event,
            (
                datetime(2020, 1, 1, 12, 30, 0, tzinfo=timezone.utc),
                datetime(2020, 1, 1, 14, 30, 0, tzinfo=timezone.utc),
                ''
            ),
            # single event with start and end within other event,
            (
                datetime(2020, 1, 1, 13, 30, 0, tzinfo=timezone.utc),
                datetime(2020, 1, 1, 14, 00, 0, tzinfo=timezone.utc),
                ''
            ),
            # recurring event, same starting date
            (

                datetime(2020, 1, 1, 12, 30, 0, tzinfo=timezone.utc),
                datetime(2020, 1, 1, 14, 30, 0, tzinfo=timezone.utc),
                'DTSTART:20200101T123000Z\nRRULE:FREQ=WEEKLY;COUNT=5;'
            ),
            # recurring event with start and end within other event,
            (
                datetime(2020, 1, 1, 13, 30, 0, tzinfo=timezone.utc),
                datetime(2020, 1, 1, 14, 00, 0, tzinfo=timezone.utc),
                'DTSTART:20200101T123000Z\nRRULE:FREQ=WEEKLY;COUNT=5;'
            ),

        ]
        for event in events:
            event_form = self.create_event_form(
                event[0],
                event[1],
                event[2],
                self.venue
            )
            self.assertFalse(event_form.is_valid())

    def test_nonconflicting_events(self):
        events = [
            # single event, starts on other events end
            (
                datetime(2020, 1, 1, 14, 30, 0, tzinfo=timezone.utc),
                datetime(2020, 1, 1, 15, 30, 0, tzinfo=timezone.utc),
                ''
            ),
            # recurring event, ends on other events start
            (

                datetime(2020, 1, 1, 11, 0, 0, tzinfo=timezone.utc),
                datetime(2020, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
                'DTSTART:20200101T123000Z\nRRULE:FREQ=WEEKLY;COUNT=5;'
            )

        ]
        for event in events:
            event_form = self.create_event_form(
                event[0],
                event[1],
                event[2],
                self.venue
            )
            self.assertTrue(event_form.is_valid())
