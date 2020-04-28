from datetime import datetime

from django.test import TestCase

from resource_hub.core.models import BankAccount, DeclarationOfIntent
from resource_hub.core.tests.test_models import TestContract

from .models import (SEPA, SEPADirectDebitPayment, SEPADirectDebitXML,
                     SEPAMandate)


class TestSEPA(TestContract):
    def setUp(self):
        super(TestSEPA, self).setUp()
        bank_account = BankAccount.objects.create(
            account_holder='joe',
            iban='NL02RABO6664435071',
            bic='INGDDEFFXXX',
        )
        self.sepa = SEPA.objects.create(
            currency='EUR',
            fee_absolute_value=0,
            fee_relative_value=0,
            fee_tax_rate=0,
            creditor_id='DE97ZZZ12345678901',
            bank_account=bank_account,
            owner=self.actor,
        )
        confirmation = DeclarationOfIntent.objects.create(
        )
        SEPAMandate.objects.create(
            creditor=self.contract.creditor,
            debitor=self.contract.debitor,
            state=SEPAMandate.STATE.RUNNING,
            confirmation=confirmation,
        )
        self.contract.payment_method = self.sepa
        self.contract.save()

    def test_xml_file(self):
        self.create_claims()
        self.contract.payment_method.is_prepayment = True
        self.contract.save()
        self.contract.settle_claims()
        payments = SEPADirectDebitPayment.objects.filter(
            state=SEPADirectDebitPayment.STATE.PENDING,
            creditor=self.contract.creditor,
        )
        self.assertEqual(len(payments), 1)
        xml_file = SEPADirectDebitXML.objects.create(
            creditor=self.contract.creditor,
            creditor_identifier=self.sepa.creditor_id,
            name=self.contract.creditor.name,
            iban=self.contract.creditor.bank_account.iban,
            bic=self.contract.creditor.bank_account.bic,
            collection_date=datetime.now().date(),
            currency='EUR'
        )
        xml_file.create_xml(payments)
        self.assertEqual(
            len(SEPADirectDebitPayment.objects.filter(
                state=SEPADirectDebitPayment.STATE.FINALIZED
            )),
            1
        )
