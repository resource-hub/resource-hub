from datetime import datetime
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from resource_hub.core.models import Claim
from resource_hub.core.tests import BaseTest
from resource_hub.venues.models import Event, VenueContract

from . import BaseVenueTest


class TestVenueContract(BaseVenueTest):
    def setUp(self):
        super(TestVenueContract, self).setUp()
        self.event = Event.objects.create(
            name='event',
            description='1',
            dtstart=datetime(2020, 1, 1, 13, 0, 0,
                             tzinfo=timezone.utc),
            dtend=datetime(2020, 1, 1, 14, 30, 0,
                           tzinfo=timezone.utc),
            dtlast=datetime(2020, 1, 1, 14, 30, 0,
                            tzinfo=timezone.utc),
            organizer=self.user,
            recurrences="DTSTART:20200101T123000Z"
        )
        self.contract = VenueContract.objects.create(
            event=self.event,
            contract_procedure=self.contract_procedure,
            payment_method=self.payment_method,
        )
        self.contract.equipment.add(self.equipment)
        self.event.venues.add(self.venue)

    def test_claims(self):
        self.contract.claim_factory(
            occurrences=self.contract.event.occurrences)
        claims = Claim.objects.filter(contract=self.contract)
        total = 0
        for claim in claims:
            total += claim.gross

        self.assertEqual(total, Decimal('25.0'))
