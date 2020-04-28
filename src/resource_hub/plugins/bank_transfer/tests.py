from datetime import datetime

from django.test import TestCase

from resource_hub.core.models import BankAccount, Payment
from resource_hub.core.tests.test_models import TestContract

from .models import BankTransfer


class TestSEPA(TestContract):
    def setUp(self):
        super(TestSEPA, self).setUp()
        bank_account = BankAccount.objects.create(
            account_holder='joe',
            iban='NL02RABO6664435071',
            bic='INGDDEFFXXX',
        )
        self.bank_transfer = BankTransfer.objects.create(
            currency='EUR',
            fee_absolute_value=0,
            fee_relative_value=0,
            fee_tax_rate=0,
            bank_account=bank_account,
            owner=self.actor,
        )
        self.contract.payment_method = self.bank_transfer
        self.contract.save()

    def test_xml_file(self):
        self.create_claims()
        self.contract.payment_method.is_prepayment = True
        self.contract.save()
        self.contract.settle_claims()
        payments = Payment.objects.filter(
            state=Payment.STATE.FINALIZED,
            creditor=self.contract.creditor,
        )
        self.assertEqual(len(payments), 1)
