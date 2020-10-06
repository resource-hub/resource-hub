from decimal import Decimal
from unittest import SkipTest

from resource_hub.core.models import BankAccount, Price
from resource_hub.core.tests import BaseTest
from resource_hub.plugins.bank_transfer.models import BankTransfer
from resource_hub.venues.models import Equipment, Venue, VenueContractProcedure


class BaseVenueTest(BaseTest):
    def setUp(self):
        super(BaseVenueTest, self).setUp()
        if self.__class__ == BaseVenueTest:
            raise SkipTest('Abstract test')
        self.venue = Venue.objects.create(
            name='Venue',
            description='nice',
            contract_procedure=self.contract_procedure,
            location=self.location,
            owner=self.user,
            base_price=Price.objects.create(
                value=Decimal('10'),
                discounts=True,
            ),
        )
        self.equipment = Equipment.objects.create(
            name='test',
            quantity=1,
            venue=self.venue,
            price=Price.objects.create(
                value=Decimal('10'),
                discounts=True,
            ),
        )
        self.contract_procedcure = VenueContractProcedure.objects.create(
            name='test contract procedure',
            auto_accept=False,
            is_invoicing=False,
            terms_and_conditions='Termns',
            termination_period=0,
            notes='Note',
            settlement_interval=7,
            owner=self.user,
        )
        self.bank_account = BankAccount.objects.create(
            account_holder='Joe',
            iban='DE89370400440532013000',
            bic='NOLADE21RDB',
        )
        self.payment_method = BankTransfer.objects.create(
            owner=self.user,
            is_prepayment=False,
            fee_absolute_value=0,
            bank_account=self.bank_account,
        )
