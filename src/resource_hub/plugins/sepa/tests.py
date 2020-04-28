from django.test import TestCase

from resource_hub.core.models import BankAccount
from resource_hub.core.tests.test_models import TestContract

from .models import SEPA, SEPAMandate


class TestSEPA(TestContract):
    def setUp(self):
        super(TestSEPA, self).setUp()
        bank_account = BankAccount.objects.create(
            account_holder='joe',
            iban='NL02RABO6664435071',
            bic='INGDDEFFXXX',
        )
        sepa = SEPA.objects.create(
            currency='EUR',
            fee_absolute_value=0,
            fee_relative_value=0,
            fee_tax_rate=0,
            creditor_id='DE97ZZZ12345678901',
            bank_account=bank_account,
            owner=self.actor,
        )
        SEPAMandate.objects.create(
            creditor=self.contract.creditor,
            debitor=self.contract.debitor,
            state=SEPAMandate.STATE.RUNNING,
        )
        self.contract.payment_method = sepa
        self.contract.save()
