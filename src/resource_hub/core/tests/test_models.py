from datetime import timedelta

from django.db.models import Min
from django.test import TestCase
from django.utils import timezone

from resource_hub.core.models import (Actor, Address, Claim, Contract,
                                      ContractProcedure, Invoice, Organization,
                                      PaymentMethod, User)

# from django.contrib.auth.models import User
# from django.utils.dateparse import parse_date

# from . import create_test_users


# class TestUser(TestCase):
#     @classmethod
#     def setUpTestData(cls):
#         create_test_users()

#     def test_person_first_name(self):
#         user = User.objects.get(username='testmate')
#         first_name = user.first_name
#         self.assertEqual('Test', first_name)


class BaseContractTest(TestCase):
    def setUp(self):
        self.settlement_interval = 7
        self.no_of_claims = 10  # only even numbers
        self.claim_length = 5

        address = Address.objects.create(
            street='test',
            street_number=12,
            postal_code='12345',
            city='test',
            country='de',
        )
        actor = User.objects.create(
            name='test',
            slug='test',
            address=address,
            email='test@test.de',
        )
        address.pk = None
        address.save()
        actor2 = Organization.objects.create(
            name='test2',
            slug='test2',
            address=address,
            email_public='joe@joe.de',
        )
        payment_method = PaymentMethod.objects.create(
            fee_absolute_value=0,
            fee_relative_value=0,
            fee_tax_rate=0,
            owner=actor,
        )
        self.contract_procedure = ContractProcedure.objects.create(
            name='test',
            tax_rate=19,
            settlement_interval=self.settlement_interval,
            owner=actor,
        )
        self.contract = Contract.objects.create(
            contract_procedure=self.contract_procedure,
            payment_method=payment_method,
            creditor=actor,
            debitor=actor2,
            state=Contract.STATE.RUNNING,
        )

        for i in range(1, self.no_of_claims + 1):
            now = timezone.now()
            length = timedelta(hours=self.claim_length)
            interval = timedelta(
                days=self.settlement_interval)
            if i > self.no_of_claims/2:
                period_start = now - interval
            else:
                period_start = now + interval
            period_end = period_start + length

            Claim.objects.create(
                contract=self.contract,
                item='test',
                quantity=i,
                unit='u',
                price=i,
                net=i*i,
                discount=0,
                discounted_net=i*i,
                tax_rate=self.contract_procedure.tax_rate,
                gross=self.contract_procedure.apply_tax(i*i),
                period_start=period_start,
                period_end=period_end,
            )


class TestContract(BaseContractTest):
    def test_legal_moves(self):
        for node, edges in Contract.STATE_GRAPH.items():
            for other_node in edges:
                self.contract.state = node
                self.contract.move_to(other_node)
                self.assertEqual(self.contract.state, other_node)

    def test_illegal_moves(self):
        state = Contract.STATE
        moves = [
            (state.INIT, state.FINALIZED),
            (state.INIT, state.RUNNING),
            (state.RUNNING, state.CANCELED),
            (state.CANCELED, state.INIT),
        ]
        for edge in moves:
            self.contract.state = edge[0]
            self.assertRaises(
                ValueError,
                self.contract.move_to, edge[1]
            )

    def test_claim_settlement(self):
        self.contract.settle_claims()
        closed_claims = self.contract.claim_set.filter(
            status=Claim.STATUS.CLOSED)
        self.assertEqual(len(closed_claims), self.no_of_claims//2)
        self.assertEqual(self.contract.state, Contract.STATE.RUNNING)

        self.contract.payment_method.is_prepayment = True
        self.contract.contract_procedure.settlement_interval += 1
        self.contract.save()
        self.contract.settle_claims()
        closed_claims = self.contract.claim_set.filter(
            status=Claim.STATUS.CLOSED)
        # test if all claims correctly closed
        self.assertEqual(len(closed_claims), self.no_of_claims)
        self.assertEqual(self.contract.state, Contract.STATE.FINALIZED)
        self.assertEqual(len(self.contract.settlement_logs.all()), 2)
        # for invoice in self.contract.invoices.all():
        #     invoice.file.delete()

    def test_inital_settlement_log(self):
        self.contract.set_initial_settlement_log()
        first_start = self.contract.claim_set.aggregate(Min('period_start'))[
            'period_start__min']
        first_log = self.contract.settlement_logs.aggregate(Min('timestamp'))[
            'timestamp__min']
        self.assertEqual(first_start, first_log)

        self.assertRaises(ValueError, self.contract.set_initial_settlement_log)

        self.contract.payment_method.is_prepayment = True
        self.contract.save()
        self.assertRaises(ValueError, self.contract.set_initial_settlement_log)

    def test_invoice_creation(self):
        self.contract.settle_claims()
        self.assertEqual(
            len(Invoice.objects.filter(contract=self.contract)),
            1
        )

    def test_invoice_settings(self):
        self.contract_procedure.is_invoicing = False
        self.contract_procedure.save()
        self.contract.settle_claims()
        self.assertEqual(
            len(Invoice.objects.filter(contract=self.contract)),
            0
        )
