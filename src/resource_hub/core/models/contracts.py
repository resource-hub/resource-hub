import uuid
from datetime import timedelta

from django.db import models, transaction
from django.db.models import Min, Q
from django.http import HttpResponse
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from ipware import get_client_ip
from model_utils.managers import InheritanceManager
from resource_hub.core.utils import build_full_url

from ..fields import CurrencyField, PercentField
from .base import BaseModel, BaseStateMachine
from .invoices import Invoice
from .notifications import Notification


class ContractProcedure(BaseModel):
    SETTLEMENT_INTERVALS = [
        (7, _('weekly')),
        (14, _('biweekly')),
        (30, _('monthly')),
    ]

    name = models.CharField(
        max_length=64,
        verbose_name=_('Name'),
        help_text=_('Give the procedure a name so you can identify it easier'),
    )
    auto_accept = models.BooleanField(
        default=False,
        verbose_name=_('Auto accept'),
        help_text=_('Automatically accept the booking?'),
    )
    is_invoicing = models.BooleanField(
        blank=True,
        default=True,
        verbose_name=_('Create invoices'),
        help_text=_('Create invoices upon settlement of claims'),
    )
    terms_and_conditions = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('terms and conditions'),
    )
    termination_period = models.IntegerField(
        default=0,
        verbose_name=_('Termination period (days)'),
        help_text=_(
            'Upon termination all claims within the termination period will be charged regardlessly'),
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Notes'),
        help_text=_(
            'This text will be added to the notification when a contract starts running')
    )
    payment_methods = models.ManyToManyField(
        'PaymentMethod',
        blank=False,
        help_text=_(
            'Choose the payment methods you want to use for this venue'),
        verbose_name=_('Payment methods'),
    )
    tax_rate = PercentField(
        default=0,
        verbose_name=_('Tax rate applied in percent'),
    )
    settlement_interval = models.IntegerField(
        choices=SETTLEMENT_INTERVALS,
        default=SETTLEMENT_INTERVALS[0][0],
        verbose_name=_('Settlement interval'),
    )
    triggers = models.ManyToManyField(
        'ContractTrigger',
        blank=True,
        related_name='procedure',
        verbose_name=_('Triggers'),
    )
    owner = models.ForeignKey(
        'Actor',
        on_delete=models.PROTECT,
        verbose_name=_('Owner'),
    )

    # attributes
    @property
    def type_name(self):
        raise NotImplementedError()

    # methods
    def __str__(self):
        return '{}: {}'.format(self.type_name, self.name)

    def apply_tax(self, net):
        return float(net) * (1 + (float(self.tax_rate)/100))


class BaseContract(BaseStateMachine):
    # constants
    class STATE(BaseStateMachine.STATE):
        # active states
        WAITING = 'w'
        RUNNING = 'r'
        DISPUTING = 'd'
        # final states
        FINALIZED = 'f'
        EXPIRED = 'x'
        CANCELED = 'c'
        DECLINED = 'n'
        TERMINATED = 't'

    STATES = [
        *BaseStateMachine.STATES,
        (STATE.WAITING, _('waiting')),
        (STATE.RUNNING, _('running')),
        (STATE.DISPUTING, _('disputing')),
        (STATE.FINALIZED, _('finalized')),
        (STATE.EXPIRED, _('expired')),
        (STATE.CANCELED, _('canceled')),
        (STATE.DECLINED, _('declined')),
        (STATE.TERMINATED, _('terminated')),
    ]

    # availabe edges for node
    STATE_GRAPH = {
        STATE.PENDING: {STATE.WAITING, STATE.CANCELED, STATE.EXPIRED, },
        STATE.WAITING: {STATE.RUNNING, STATE.DECLINED, },
        STATE.RUNNING: {STATE.DISPUTING, STATE.FINALIZED, STATE.TERMINATED, },
        STATE.DISPUTING: {STATE.RUNNING, STATE.FINALIZED, },
    }

    # fields
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('UUID'),
    )
    contract_procedure = models.ForeignKey(
        'ContractProcedure',
        on_delete=models.PROTECT,
        null=True,
        verbose_name=_('Contract Procedure'),
    )
    terms_and_conditions = models.TextField(
        null=True,
        verbose_name=_('Terms and conditions'),
    )
    termination_period = models.IntegerField(
        default=0,
        verbose_name=_('Termination period'),
    )
    creditor = models.ForeignKey(
        'Actor',
        null=True,
        on_delete=models.SET_NULL,
        related_name='creditor',
        verbose_name=_('Creditor'),
    )
    debitor = models.ForeignKey(
        'Actor',
        null=True,
        on_delete=models.SET_NULL,
        related_name='debitor',
        verbose_name=_('Debitor'),
    )
    # fields
    is_fixed_term = models.BooleanField(
        default=True,
        verbose_name=_('Is fixed term'),
    )
    payment_method = models.ForeignKey(
        'PaymentMethod',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Payment method'),
    )
    price_profile = models.ForeignKey(
        'PriceProfile',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        verbose_name=_('Price profile'),
    )
    confirmation = models.OneToOneField(
        'DeclarationOfIntent',
        null=True,
        on_delete=models.SET_NULL,
        related_name='contract_confirmation',
        verbose_name=_('Confirmation'),
    )
    acceptance = models.OneToOneField(
        'DeclarationOfIntent',
        on_delete=models.SET_NULL,
        null=True,
        related_name='contract_acceptance',
        verbose_name=_('Acceptance'),
    )
    created_by = models.ForeignKey(
        'User',
        related_name='contract_created_by',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Created by'),
    )

    # attributes
    class Meta:
        abstract = True

    @property
    def verbose_name(self) -> str:
        raise NotImplementedError()

    @property
    def is_pending(self) -> bool:
        return self.state == self.STATE.PENDING

    @property
    def overview(self) -> str:
        '''
        Returns description (may use html) of the contents of the contract
        '''
        raise NotImplementedError()

    @property
    def is_self_dealing(self):
        return self.creditor == self.debitor

    def call_triggers(self, state):
        pass

    def create_confirmation(self, request):
        self.confirmation = DeclarationOfIntent.create(
            request=request,
        )

    def create_acceptance(self, request):
        self.acceptance = DeclarationOfIntent.create(
            request=request,
        )
    # state setters

    def set_pending(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def set_expired(self) -> None:
        raise NotImplementedError()

    def set_cancelled(self) -> None:
        raise NotImplementedError()

    def set_declined(self, request) -> None:
        raise NotImplementedError()

    def set_waiting(self, request) -> None:
        raise NotImplementedError()

    def set_running(self, request) -> None:
        raise NotImplementedError()

    def set_finalized(self) -> None:
        raise NotImplementedError()


class DeclarationOfIntent(models.Model):
    # fields
    user = models.ForeignKey(
        'User',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('User'),
    )
    ip = models.GenericIPAddressField(
        null=True,
        verbose_name=_('IP'),
    )
    ip_routable = models.BooleanField(
        default=True,
        verbose_name=_('IP routable'),
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Timestamp'),
    )

    @classmethod
    def create(cls, request):
        client_ip, is_routable = get_client_ip(request)
        if client_ip is None:
            # Unable to get the client's IP address
            ip_routable = False
        else:
            # We got the client's IP address
            ip_routable = is_routable
        return cls.objects.create(
            user=request.user,
            ip=client_ip,
            ip_routable=ip_routable
        )


class Contract(BaseContract):
    @property
    def verbose_name(self) -> str:
        return _('Contract')

    @property
    def is_pending(self) -> bool:
        return self.state == self.STATE.PENDING

    @property
    def expiration_period(self) -> int:
        return 30

    @property
    def is_expired(self) -> bool:
        delta = (timedelta(
            minutes=self.expiration_period) - (timezone.now() - self.created_at))
        return delta.total_seconds() <= 0

    @property
    def overview(self) -> str:
        '''
        Returns description (may use html) of the contents of the contract
        '''
        raise NotImplementedError()

    @property
    def claim_table(self):
        from ..tables import ClaimTable
        claims = self.claim_set.all()
        if claims:
            return ClaimTable(claims)
        return ''

    # methods
    def set_initial_settlement_log(self):
        if self.payment_method.is_prepayment:
            raise ValueError(
                'initial settlement logs cannot be set for prepayments')
        if self.settlement_logs.exists():
            raise ValueError('there already is a settlement log entry')
        smallest_start = self.claim_set.aggregate(Min('period_start'))
        self.settlement_logs.create(
            timestamp=smallest_start['period_start__min'])

    def call_triggers(self, state):
        return
    # notifications

    def _send_state_notification(self, type_, sender, recipient, header, message='', attachments=None, request=None):
        if self.creditor != self.debitor:
            return Notification.build(
                type_=type_,
                sender=sender,
                recipient=recipient,
                header=header,
                message=message,
                link=build_full_url(reverse('control:finance_contracts_manage_details',
                                            kwargs={'pk': self.pk}), request=request),
                level=Notification.LEVEL.MEDIUM,
                target=self,
                attachments=attachments,
            )

    def _get_waiting_notification_msg(self):
        return ''

    def _send_waiting_notification(self, request):
        self._send_state_notification(
            type_=Notification.TYPE.CONTRACT_CREATED,
            sender=self.debitor,
            recipient=self.creditor,
            header=_('{debitor} created {contract}'.format(
                debitor=self.debitor,
                contract=self.verbose_name,
            )),
            request=request,
            message=self._get_waiting_notification_msg(),
        )

    def _get_running_notification_msg(self):
        return self.contract_procedure.notes

    def _get_running_notification_attachments(self):
        return None

    def _send_running_notification(self, request):
        self._send_state_notification(
            type_=Notification.TYPE.CONTRACT_ACCEPTED,
            sender=self.creditor,
            recipient=self.debitor,
            header=_('{creditor} accepted {contract}'.format(
                creditor=self.creditor,
                contract=self.verbose_name,
            )),
            message=self._get_running_notification_msg(),
            request=request,
            attachments=self._get_running_notification_attachments(),
        )

    def _send_declined_notification(self, request):
        self._send_state_notification(
            type_=Notification.TYPE.CONTRACT_DECLINED,
            sender=self.creditor,
            recipient=self.debitor,
            header=_('{creditor} declined {contract}'.format(
                creditor=self.creditor,
                contract=self.verbose_name,
            )),
            request=request,
        )

    def _send_terminated_notification(self, initiator, reciever):
        self._send_state_notification(
            type_=Notification.TYPE.CONTRACT_TERMINATED,
            sender=initiator,
            recipient=reciever,
            header=_('{initiator} terminated {contract}'.format(
                initiator=initiator,
                contract=self.verbose_name,
            )),
        )

    def purge(self) -> None:
        self.claim_set.all().soft_delete()

    # state setters
    def move_to(self, state):
        if self.state in self.STATE_GRAPH and state in self.STATE_GRAPH[self.state]:
            self.call_triggers(state)
            self.state = state
        else:
            raise ValueError('Cannot move from state {} to state {}'.format(
                self.get_state_display(), state))

    # active states
    def set_pending(self, *args, **kwargs) -> None:
        self.move_to(self.STATE.PENDING)
        self.save()

    def set_waiting(self, request) -> None:
        self.move_to(self.STATE.WAITING)
        self.create_confirmation(request)
        self.save()
        self._send_waiting_notification(request)
        if self.contract_procedure.auto_accept or (self.creditor == self.debitor):
            self.set_running(request)

    def set_running(self, request) -> None:
        self.move_to(self.STATE.RUNNING)
        if self.contract_procedure.auto_accept or self.debitor == self.creditor:
            pass
        else:
            self.create_acceptance(request)
        if self.payment_method.is_prepayment or self.debitor == self.creditor:
            self.settle_claims()
        else:
            self.set_initial_settlement_log()
        self.save()
        self._send_running_notification(request)
    # final states

    def set_finalized(self) -> None:
        self.move_to(self.STATE.FINALIZED)
        self.save()

    def set_expired(self) -> None:
        self.move_to(self.STATE.EXPIRED)
        self.purge()
        self.save()

    def set_cancelled(self) -> None:
        self.move_to(self.STATE.CANCELED)
        self.purge()
        self.save()

    def set_declined(self, request) -> None:
        self.move_to(self.STATE.DECLINED)
        self.save()
        self._send_declined_notification(request)

    def set_terminated(self, initiator) -> None:
        self.move_to(self.STATE.TERMINATED)
        query = Q(state=Claim.STATE.PENDING)
        query.add(Q(contract=self), Q.AND)
        if self.termination_period > 0:
            selector = timezone.now() + timedelta(days=self.termination_period)
            query.add(Q(period_start__gte=selector), Q.AND)
        Claim.objects.filter(query).update(state=Claim.STATE.TERMINATED)
        self.save()
        reciever = self.creditor if self.debitor == initiator else self.debitor
        self._send_terminated_notification(initiator, reciever)

    def claim_factory(self, **kwargs):
        if self.is_self_dealing:
            return

    def create_fee_claims(self, net_total, currency, start, end):
        if net_total > 0 and (self.payment_method.fee_absolute_value > 0 or self.payment_method.fee_relative_value > 0):
            net_fee = self.payment_method.apply_fee(net_total)
            discounted_net_fee = self.price_profile.apply(
                net_fee
            ) if self.price_profile else net_fee
            gross_fee = self.payment_method.apply_fee_tax(
                discounted_net_fee)

            Claim.objects.create(
                contract=self,
                item=self.payment_method.verbose_name,
                quantity=1,
                unit='u',
                price=net_fee,
                currency=currency,
                net=net_fee,
                discount=self.price_profile.discount if self.price_profile else 0,
                discounted_net=discounted_net_fee,
                tax_rate=self.payment_method.fee_tax_rate,
                gross=gross_fee,
                period_start=start,
                period_end=end,
            )

    def settle_claims(self):
        now = timezone.now()
        selector = now + \
            timedelta(
                days=self.contract_procedure.settlement_interval
            ) if self.payment_method.is_prepayment else now
        open_claims = self.claim_set.filter(
            state=Claim.STATE.PENDING, period_end__lte=selector)
        if open_claims:
            with transaction.atomic():
                payment_method = PaymentMethod.objects.get_subclass(
                    pk=self.payment_method.pk)
                if self.contract_procedure.is_invoicing:
                    invoice = Invoice.build(self, open_claims)
                    invoice.create_pdf()
                else:
                    invoice = None

                payment_method.settle(self, open_claims, invoice)
                open_claims.update(state=Claim.STATE.SETTLED)
        if self.is_fixed_term:
            if not self.claim_set.filter(state=Claim.STATE.PENDING).exists():
                self.set_finalized()
        self.settlement_logs.create()


class SettlementLog(BaseModel):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='settlement_logs',
        verbose_name=_('Contract'),
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Timestamp'),
    )


class Claim(BaseStateMachine):
    class STATE(BaseStateMachine.STATE):
        SETTLED = 's'
        TERMINATED = 't'

    STATES = [
        *BaseStateMachine.STATES,
        (STATE.SETTLED, _('closed')),
        (STATE.TERMINATED, _('terminated')),
    ]

    STATE_GRAPH = {
        STATE.PENDING: {STATE.SETTLED, STATE.TERMINATED}
    }

    contract = models.ForeignKey(
        Contract,
        on_delete=models.PROTECT,
        verbose_name=_('Contract'),
    )
    item = models.CharField(
        max_length=255,
        verbose_name=_('Item'),
    )
    quantity = models.DecimalField(
        decimal_places=5,
        max_digits=15,
        verbose_name=_('Quantity'),
    )
    unit = models.CharField(
        max_length=5,
        verbose_name=_('Unit'),
    )
    price = models.DecimalField(
        decimal_places=5,
        max_digits=15,
        verbose_name=_('Price'),
    )
    currency = CurrencyField()
    net = models.DecimalField(
        decimal_places=5,
        max_digits=15,
        verbose_name=_('Net'),
    )
    discount = PercentField(
        verbose_name=_('Discount'),
    )
    discounted_net = models.DecimalField(
        decimal_places=5,
        max_digits=15,
        verbose_name=_('Discounted net'),
    )
    tax_rate = PercentField(
        verbose_name=_('Tax rate applied in percent'),
    )
    gross = models.DecimalField(
        decimal_places=5,
        max_digits=15,
        verbose_name=_('Gross'),
    )
    period_start = models.DateTimeField(
        verbose_name=_('Performance period start'),
    )
    period_end = models.DateTimeField(
        verbose_name=_('Performance period end'),
    )


class Trigger(BaseModel):
    condition = models.CharField(
        choices=Contract.STATES,
        max_length=2,
        verbose_name=_('Condition'),
    )
    name = models.CharField(
        max_length=64,
        verbose_name=_('Name'),
    )
    comment = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Comment'),
    )
    owner = models.ForeignKey(
        'Actor',
        on_delete=models.CASCADE,
        verbose_name=_('Owner'),
    )

    class Meta:
        abstract = True

    # attributes
    @property
    def fixed_condtion(self) -> bool:
        return False

    @property
    def default_condition(self) -> str:
        raise NotImplementedError()

    @property
    def verbose_name(self) -> str:
        raise NotImplementedError()

    @property
    def info(self) -> dict:
        return {
            'name': '',
            'provider': '',
            'description': '',
            'thumbnail': 'images/default.png',
        }

    # methods
    def callback(self) -> None:
        raise NotImplementedError()

    def form(self):
        raise NotImplementedError()

    def __str__(self):
        return '{}: {} ({})'.format(self.verbose_name, self.name, self.comment)


class ContractTrigger(Trigger):
    # attributes
    @staticmethod
    def fixed_condtion() -> bool:
        return False

    @staticmethod
    def default_condition() -> str:
        return Contract.STATE.RUNNING


class PaymentMethod(Trigger):
    # fields
    currency = CurrencyField()
    is_prepayment = models.BooleanField(
        default=False,
        verbose_name=_('Prepayment?'),
        help_text=_(
            'If activated, claims within the following settlement interval are charged in advance')
    )
    fee_absolute_value = models.IntegerField(
        default=0,
        verbose_name=_('Absolute fee'),
        help_text=_('A constant value that is added to every transaction')
    )
    fee_relative_value = PercentField(
        default=0,
        verbose_name=_('Relative fee (%)'),
        help_text=_(
            'A relative value that is based on the total value of a transaction')
    )
    fee_tax_rate = PercentField(
        default=0,
        verbose_name=_('Tax rate applied to payement fee (%)'),
    )

    def __str__(self):
        prepayment = _('(prepayment)') if self.is_prepayment else ''
        return '{} {}: {}{} + {}%'.format(self.verbose_name, prepayment, self.fee_absolute_value, self.currency, self.fee_relative_value)

    # methods
    def initialize(self, contract, request) -> HttpResponse:
        raise NotImplementedError()

    def settle(self, contract, claims, invoice) -> None:
        pass

    def apply_fee(self, net) -> float:
        total = self.fee_absolute_value
        total += float(net) * (float(self.fee_relative_value/100))
        return total

    def apply_fee_tax(self, net) -> float:
        return float(net) * (1 + (float(self.fee_tax_rate)/100))

    def get_invoice_text(self) -> str:
        '''
        text appended to the end of invoices informing about the payment, possibly further instructions
        '''
        return ''
