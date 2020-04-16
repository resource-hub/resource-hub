from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from resource_hub.core.models import (Actor, Address, Claim, Contract,
                                      ContractProcedure, Organization,
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

class TestContract(TestCase):
    def setUp(self):
        self.settlement_interval = 7
        address = Address.objects.create(
            street='test',
            street_number=12,
            postal_code='12345',
            city='test',
            country='test',
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
            fee_absolute=False,
            fee_value=0,
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
        )

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
        n = 10

        for i in range(1, n + 1):
            now = timezone.now()
            interval = timedelta(days=self.settlement_interval)
            length = timedelta(hours=5)
            if i > n/2:
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
        self.contract.settle_claims()
        closed_claims = self.contract.claim_set.filter(
            status=Claim.STATUS.CLOSED)
        self.assertEqual(len(closed_claims), n//2)
        # for invoice in self.contract.invoices.all():
        #     invoice.file.delete()

        # invoice = Invoice.objects.get(contract=self.contract)
