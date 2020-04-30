from datetime import timedelta

from django.db.models import Min
from django.test import Client, TestCase
from django.utils import timezone

from resource_hub.core.models import (Address, BankAccount, Claim, Contract,
                                      ContractProcedure, Invoice, Notification,
                                      Organization, PaymentMethod, User)


def create_users():
    bank_account = BankAccount.objects.create(
        account_holder='joe',
        iban='NL02RABO6664435071',
        bic='INGDDEFFXXX',
    )
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
        bank_account=bank_account,
    )
    address.pk = None
    address.save()
    bank_account.pk = None
    bank_account.save()
    actor2 = Organization.objects.create(
        name='test2',
        slug='test2',
        address=address,
        email_public='joe@joe.de',
        bank_account=bank_account,
    )
    return actor, actor2


class BaseContractTest(TestCase):
    def setUp(self):
        self.settlement_interval = 7
        self.no_of_claims = 10  # only even numbers
        self.claim_length = 5

        self.actor, self.actor2 = create_users()
        payment_method = PaymentMethod.objects.create(
            fee_absolute_value=0,
            fee_relative_value=0,
            fee_tax_rate=0,
            owner=self.actor,
        )
        self.contract_procedure = ContractProcedure.objects.create(
            name='test',
            tax_rate=19,
            settlement_interval=self.settlement_interval,
            owner=self.actor,
        )
        self.contract = Contract.objects.create(
            contract_procedure=self.contract_procedure,
            payment_method=payment_method,
            creditor=self.actor,
            debitor=self.actor2,
            state=Contract.STATE.RUNNING,
        )

    def create_claims(self):
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
                state=Claim.STATE.PENDING,
                contract=self.contract,
                item='test',
                quantity=i,
                unit='u',
                price=i,
                net=i*i,
                discount=0,
                discounted_net=i*i,
                tax_rate=self.contract.contract_procedure.tax_rate,
                gross=self.contract.contract_procedure.apply_tax(i*i),
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
            (state.PENDING, state.FINALIZED),
            (state.PENDING, state.TERMINATED),
            (state.RUNNING, state.CANCELED),
            (state.CANCELED, state.PENDING),
        ]
        for edge in moves:
            self.contract.state = edge[0]
            self.assertRaises(
                ValueError,
                self.contract.move_to, edge[1]
            )

    def test_claim_settlement(self):
        self.create_claims()
        self.contract.settle_claims()
        closed_claims = self.contract.claim_set.filter(
            state=Claim.STATE.SETTLED)
        self.assertEqual(len(closed_claims), self.no_of_claims//2)
        self.assertEqual(self.contract.state, Contract.STATE.RUNNING)

        self.contract.payment_method.is_prepayment = True
        self.contract.contract_procedure.settlement_interval += 1
        self.contract.save()
        self.contract.settle_claims()
        closed_claims = self.contract.claim_set.filter(
            state=Claim.STATE.SETTLED)
        # test if all claims correctly closed
        self.assertEqual(len(closed_claims), self.no_of_claims)
        self.assertEqual(self.contract.state, Contract.STATE.FINALIZED)
        self.assertEqual(len(self.contract.settlement_logs.all()), 2)
        Notification.send_open_mails()
        for invoice in self.contract.invoices.all():
            invoice.file.delete()

    def test_inital_settlement_log(self):
        self.create_claims()
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
        self.create_claims()
        self.contract.settle_claims()
        self.assertEqual(
            len(Invoice.objects.filter(contract=self.contract)),
            1
        )

    def test_self_dealing(self):
        self.contract.debitor = self.actor
        self.contract.state = Contract.STATE.PENDING
        self.contract.save()
        client = Client()
        response = client.get('')
        request = response.wsgi_request
        request.user = User.objects.create_user(
            username='test',
            email='test2@test.de',
            password='12Test12',
        )
        self.contract.set_waiting(request)
        self.assertEqual(self.contract.state, Contract.STATE.FINALIZED)

    def test_invoice_settings(self):
        self.create_claims()
        self.contract_procedure.is_invoicing = False
        self.contract_procedure.save()
        self.contract.settle_claims()
        self.assertEqual(
            len(Invoice.objects.filter(contract=self.contract)),
            0
        )

    def test_send_state_notifications(self):
        sender = self.contract.creditor
        recipient = self.contract.debitor
        header = 'test'
        message = 'test'
        notification = self.contract._send_state_notification(
            sender, recipient, header, message
        )
        self.assertEqual(notification.sender, sender)
        self.assertEqual(notification.recipient, recipient)
        self.assertEqual(notification.header, header)
        self.assertEqual(notification.message, message)

        self.contract.debitor = self.contract.creditor
        self.contract.save()
        notification = self.contract._send_state_notification(
            sender, recipient, header, message
        )
        self.assertIsNone(notification)

    def test_set_terminated(self):
        self.create_claims()
        self.contract.settle_claims()
        self.contract.set_terminated(self.actor)
        terminated_claims = self.contract.claim_set.filter(
            state=Claim.STATE.TERMINATED
        )
        self.assertEqual(len(terminated_claims), self.no_of_claims//2)

    def test_set_terminated_with_perioda(self):
        self.contract.termination_period = self.settlement_interval + 1
        self.create_claims()
        self.contract.settle_claims()
        self.contract.set_terminated(self.actor)
        terminated_claims = self.contract.claim_set.filter(
            state=Claim.STATE.TERMINATED
        )
        self.assertEqual(len(terminated_claims), 0)


class TestNotification(TestCase):
    def setUp(self):
        actor, actor2 = create_users()
        Notification.build(
            type_=Notification.TYPE.INFO,
            sender=actor,
            recipient=actor2,
            header='test',
            message='test',
            link='',
            level=Notification.LEVEL.MEDIUM,
            target=actor,
            attachments=['media/images/default.png',
                         'media/images/logo.png'],
        )

    def test_send_open_mails(self):
        Notification.send_open_mails()
        for notification in Notification.objects.all():
            self.assertEqual(notification.state, Notification.STATE.SENT)
