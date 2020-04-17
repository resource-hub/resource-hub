import string
import uuid
from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.files.base import ContentFile
from django.db import DatabaseError, models, transaction
from django.db.models import Max, Min
from django.db.models.functions import Cast
from django.http import HttpResponse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import pgettext
from django.utils.translation import ugettext_lazy as _

import pycountry
from django_countries.fields import CountryField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from ipware import get_client_ip
from model_utils.fields import MonitorField
from model_utils.managers import InheritanceManager

from .fields import PercentField
from .renderer import InvoiceRenderer
from .settings import COUNTRIES_WITH_STATE_IN_ADDRESS, CURRENCIES
from .utils import get_valid_slug, language


class BaseModel(models.Model):
    # fields
    is_deleted = models.BooleanField(
        default=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        abstract = True

    # methods
    def soft_delete(self):
        self.is_deleted = True
        self.save()


class Actor(BaseModel):
    # Fields
    name = models.CharField(
        max_length=128,
        null=True,
    )
    slug = models.SlugField(
        unique=True,
        db_index=True,
        max_length=50,
    )
    address = models.OneToOneField(
        'Address',
        null=True,
        on_delete=models.SET_NULL,
    )
    bank_account = models.OneToOneField(
        'BankAccount',
        null=True,
        on_delete=models.SET_NULL,
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='images/',
        default='images/default.png',
    )
    thumbnail = ImageSpecField(
        source='image',
        processors=[ResizeToFill(100, 100)],
        format='PNG',
        options={
            'quality': 60,
        },
    )
    thumbnail_small = ImageSpecField(
        source='image',
        processors=[ResizeToFill(40, 40)],
        format='PNG',
        options={
            'quality': 60,
        }
    )
    thumbnail_large = ImageSpecField(
        source='image',
        processors=[
            ResizeToFill(300, 300),
        ],
        format='PNG',
        options={
            'quality': 90,
        }
    )
    telephone_private = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    telephone_public = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )
    email_public = models.EmailField(
        null=True,
        blank=True,
    )
    website = models.URLField(
        null=True,
        blank=True,
    )
    info_text = models.TextField(
        null=True,
        blank=True,
    )
    # setting fields
    tax_id = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )
    vat_id = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )
    invoice_numbers_prefix = models.CharField(
        max_length=5,
        default='RH',
    )
    invoice_numbers_prefix_cancellations = models.CharField(
        max_length=5,
        default='CAN',
    )
    invoice_introductory_text = models.TextField(
        null=True,
        blank=True,
        default='',
    )
    invoice_additional_text = models.TextField(
        null=True,
        blank=True,
        default='',
    )
    invoice_footer_text = models.TextField(
        null=True,
        blank=True,
        default='',
    )
    invoice_logo_image = models.ImageField(
        null=True,
        blank=True,
        upload_to='images/',
        default='images/logo.png',
    )
    objects = InheritanceManager()

    @property
    def notification_recipients(self) -> list:
        raise NotImplementedError()
    # Metadata

    class Meta:
        ordering = ['id']

    # Methods
    def __str__(self):
        return str(self.name)


class User(AbstractUser, Actor):
    """
    natural person
    """
    email = models.EmailField(
        unique=True,
    )
    birth_date = models.DateField(
        null=True,
    )

    @property
    def notification_recipients(self) -> list:
        return [self.email, ]

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = get_valid_slug(self, self.username)

        super(User, self).save(*args, **kwargs)


class Organization(Actor):
    """
    juristic person
    """

    # fields
    members = models.ManyToManyField(
        User,
        through='OrganizationMember',
    )
    created_by = models.ForeignKey(
        User,
        related_name='organization_created_by',
        null=True,
        on_delete=models.SET_NULL,
    )

    @property
    def notification_recipients(self) -> list:
        return [self.email_public, ]
    # Methods

    def __str__(self):
        return super().name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = get_valid_slug(self, self.name)
        super(Organization, self).save(*args, **kwargs)


class Address(models.Model):
    """
    describe address
    """

    # Fields
    street = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    street_number = models.CharField(
        max_length=10,
        null=True,
        blank=True,
    )
    postal_code = models.CharField(
        max_length=5,
        null=True,
        blank=True,
    )
    city = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )
    country = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        related_name='address_updated_by',
        on_delete=models.SET_NULL,
    )

    # Metadata
    class Meta:
        ordering = ['postal_code', 'street']

    # Methods
    def __str__(self):
        return '{} {}, {} {}'.format(
            self.street,
            self.street_number,
            self.postal_code,
            self.city
        )


class BankAccount(models.Model):
    """
    describes a bank account
    """

    # Fields
    account_holder = models.CharField(
        max_length=128,
        null=True,
        blank=True,
    )
    iban = models.CharField(
        max_length=40,
        null=True,
        blank=True,
    )
    bic = models.CharField(
        max_length=11,
        null=True,
        blank=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        related_name='bank_account_updated_by',
        on_delete=models.SET_NULL,
    )

    # Metadata

    class Meta:
        ordering = ['bic', 'iban', ]

    # Methods
    def __str__(self):
        return '{} with account {} at {}'.format(
            self.account_holder,
            self.iban,
            self.bic
        )


class Location(models.Model):
    """
    describing locations
    """

    # Fields
    slug = models.SlugField(
        max_length=50,
        unique=True,
        db_index=True,
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE
    )
    name = models.CharField(
        unique=True,
        max_length=128,
        null=True,
        blank=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        default=0,
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        default=0
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='images/',
        default='images/default.png',
    )
    thumbnail = ImageSpecField(
        source='image',
        processors=[
            ResizeToFill(400, 300),
        ],
        format='PNG',
        options={
            'quality': 60,
        }
    )
    is_public = models.BooleanField(default=True)
    owner = models.ForeignKey(
        Actor,
        on_delete=models.CASCADE,
    )
    created_at = models.DateField(
        auto_now_add=True,
    )
    created_by = models.ForeignKey(
        User,
        null=True,
        related_name='location_created_by',
        on_delete=models.SET_NULL,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    updated_by = models.ForeignKey(
        User,
        null=True,
        related_name='location_updated_by',
        on_delete=models.SET_NULL,
    )

    # Metadata
    class Meta:
        ordering = ['name']

    # Methods
    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = get_valid_slug(self, self.name)

        super(Location, self).save(*args, **kwargs)


class OrganizationMember(models.Model):
    """member of organization."""

    # constants
    MEMBER = 0
    ADMIN = 1
    OWNER = 2

    ORGANIZATION_ROLES = [
        (MEMBER, _('member')),
        (ADMIN, _('administrator')),
        (OWNER, _('owner')),
    ]

    # fields
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )
    role = models.IntegerField(
        choices=ORGANIZATION_ROLES,
        default=MEMBER,
        null=False,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        unique_together = ('organization', 'user',)

    def is_admin(self) -> bool:
        if self.role == OrganizationMember.ADMIN or self.role == OrganizationMember.OWNER:
            return True
        else:
            return False

    @staticmethod
    def role_display_reverse(val: int) -> str:
        for item in OrganizationMember.ORGANIZATION_ROLES:
            if item[0] == val:
                return item[1]
        raise ValueError('Corresponding role does not exist')

    @staticmethod
    def get_role(user, organization) -> str:
        role = OrganizationMember.objects.get(
            organization=organization,
            user=user
        ).get_role_display()
        return role


class Notification(BaseModel):
    class ACTION:
        CREATE = 'c'
        BOOK = 'b'
        CONFIRM = 'co'

    class LEVEL:
        LOW = 0  # info
        MEDIUM = 1  # action required, mail
        HIGH = 2  # warning
        CRITICAL = 3  # mandatory information

    ACTIONS = [
        (ACTION.CREATE, _('created')),
        (ACTION.BOOK, _('booked')),
        (ACTION.CONFIRM, _('confirmed')),
    ]
    LEVELS = [
        (LEVEL.LOW, _('low')),
        (LEVEL.MEDIUM, _('medium')),
        (LEVEL.HIGH, _('high')),
        (LEVEL.CRITICAL, _('critical')),
    ]
    sender = models.ForeignKey(
        Actor,
        null=True,
        on_delete=models.SET_NULL,
        related_name='notification_sender',
    )
    action = models.CharField(
        choices=ACTIONS,
        max_length=3,
    )
    target = models.CharField(
        max_length=255,
    )
    link = models.URLField()
    recipient = models.ForeignKey(
        Actor,
        on_delete=models.PROTECT,
        related_name='notification_recipient',
    )
    level = models.CharField(
        choices=LEVELS,
        max_length=3,
    )
    message = models.TextField()
    is_read = models.BooleanField(
        default=False,
    )


class Payment(models.Model):
    # constants
    CREATED = 'c'
    PENDING = 'p'
    FINALIZED = 'f'
    FAILED = 'fa'
    CANCELED = 'ca'
    REFUNDED = 'r'

    STATES = [
        (PENDING, _('pending')),
        (FINALIZED, _('finalized')),
        (FAILED, _('failed')),
        (CANCELED, _('canceled')),
        (REFUNDED, _('refunded')),
    ]

    # fields
    state = models.CharField(
        choices=STATES,
        max_length=2,
    )
    state_changed = MonitorField(monitor='state')
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('payment notes'),
    )
    payment_date = models.DateTimeField(
        null=True,
        blank=True,
    )
    payment_method = models.ForeignKey(
        'PaymentMethod',
        null=True,
        on_delete=models.SET_NULL,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )


class DeclarationOfIntent(models.Model):
    # fields
    user = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
    )
    ip = models.GenericIPAddressField(
        null=True,
    )
    ip_routable = models.BooleanField(
        default=True,
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
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


class Price(models.Model):
    addressee = models.ForeignKey(
        Actor,
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE,
    )
    value = models.DecimalField(
        decimal_places=5,
        max_digits=15,
        verbose_name=_('Price'),
    )
    currency = models.CharField(
        default='EUR',
        choices=CURRENCIES,
        max_length=5,
    )
    discounts = models.BooleanField(
        default=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return '{} {}'.format(self.value.normalize(), self.currency)


class PriceProfile(models.Model):
    contract_procedure = models.ForeignKey(
        'ContractProcedure',
        on_delete=models.PROTECT,
    )
    addressee = models.ForeignKey(
        Actor,
        null=True,
        blank=True,
        default=None,
        on_delete=models.CASCADE
    )
    description = models.CharField(
        max_length=64,
    )
    discount = PercentField()

    # methods
    def __str__(self):
        addressee = '' if self.addressee is None else '({})'.format(
            self.addressee.name)
        return '{}%: {} {}'.format(self.discount, self.description, addressee)

    def apply(self, net):
        return float(net) * (1 - (float(self.discount)/100))


class BaseContract(BaseModel):
    # constants
    class STATE:
        INIT = 'i'
        # active states
        PENDING = 'p'
        WAITING = 'w'
        RUNNING = 'r'
        DISPUTING = 'd'
        # final states
        FINALIZED = 'f'
        EXPIRED = 'x'
        CANCELED = 'c'
        DECLINED = 'n'

    STATES = [
        (STATE.INIT, _('initializing')),
        (STATE.PENDING, _('pending')),
        (STATE.WAITING, _('waiting')),
        (STATE.RUNNING, _('running')),
        (STATE.DISPUTING, _('disputing')),
        (STATE.FINALIZED, _('finalized')),
        (STATE.EXPIRED, _('expired')),
        (STATE.CANCELED, _('canceled')),
        (STATE.DECLINED, _('declined')),
    ]

    # availabe edges for node
    STATE_GRAPH = {
        STATE.INIT: [STATE.PENDING],
        STATE.PENDING: [STATE.WAITING, STATE.CANCELED, STATE.EXPIRED, ],
        STATE.WAITING: [STATE.RUNNING, STATE.DECLINED, ],
        STATE.RUNNING: [STATE.DISPUTING, STATE.FINALIZED, ],
        STATE.DISPUTING: [STATE.RUNNING, STATE.FINALIZED, ]
    }

    # fields
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
    )
    contract_procedure = models.ForeignKey(
        'ContractProcedure',
        on_delete=models.PROTECT,
        null=True,
    )
    creditor = models.ForeignKey(
        Actor,
        null=True,
        on_delete=models.SET_NULL,
        related_name='creditor',
    )
    debitor = models.ForeignKey(
        Actor,
        null=True,
        on_delete=models.SET_NULL,
        related_name='debitor',
    )
    state = models.CharField(
        choices=STATES,
        max_length=2,
        default=STATE.INIT,
    )
    state_changed = MonitorField(monitor='state')
    # fields
    is_fixed_term = models.BooleanField(
        default=True
    )
    payment_method = models.ForeignKey(
        'PaymentMethod',
        null=True,
        on_delete=models.SET_NULL,
    )
    price_profile = models.ForeignKey(
        PriceProfile,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    confirmation = models.OneToOneField(
        DeclarationOfIntent,
        null=True,
        on_delete=models.SET_NULL,
        related_name='contract_confirmation',
    )
    acceptance = models.OneToOneField(
        DeclarationOfIntent,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contract_acceptance',
    )
    created_by = models.ForeignKey(
        User,
        related_name='contract_created_by',
        null=True,
        on_delete=models.SET_NULL,
    )

    # attributes
    objects = InheritanceManager()

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
    def move_to(self, state):
        if self.state in self.STATE_GRAPH and state in self.STATE_GRAPH[self.state]:
            self.call_triggers(state)
            self.state = state
        else:
            raise ValueError('Cannot move from state {} to state {}'.format(
                self.get_state_display(), state))

    def set_pending(self, *args, **kwargs) -> None:
        raise NotImplementedError()

    def set_expired(self) -> None:
        raise NotImplementedError()

    def set_cancelled(self) -> None:
        raise NotImplementedError()

    def set_declined(self) -> None:
        raise NotImplementedError()

    def set_waiting(self, request) -> None:
        raise NotImplementedError()

    def set_running(self, request) -> None:
        raise NotImplementedError()

    def set_finalized(self) -> None:
        raise NotImplementedError()


class Contract(BaseContract):
    @property
    def verbose_name(self) -> str:
        raise NotImplementedError()

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
        from .tables import ClaimTable
        claims = self.claim_set.all()
        if claims:
            return ClaimTable(claims)
        return ''

    # methods
    def set_initial_settlement_log(self):
        if self.payment_method.is_prepayment:
            raise ValueError(
                'initial settlement logs cannot be set for prepayments')
        if len(self.settlement_logs.all()) > 0:
            raise ValueError('there already is a settlement log entry')
        smallest_start = self.claim_set.aggregate(Min('period_start'))
        self.settlement_logs.create(
            timestamp=smallest_start['period_start__min'])

    def call_triggers(self, state):
        return

    # state setters
    def move_to(self, state):
        if self.state in self.STATE_GRAPH and state in self.STATE_GRAPH[self.state]:
            self.call_triggers(state)
            self.state = state
        else:
            raise ValueError('Cannot move from state {} to state {}'.format(
                self.get_state_display(), state))

    def set_pending(self, *args, **kwargs) -> None:
        self.move_to(self.STATE.PENDING)
        if self.creditor != self.debitor:
            self.claim_factory(**kwargs)
        self.save()

    def set_expired(self) -> None:
        self.move_to(self.STATE.EXPIRED)
        self.save()

    def set_cancelled(self) -> None:
        self.move_to(self.STATE.CANCELED)
        self.save()

    def set_declined(self) -> None:
        self.move_to(self.STATE.DECLINED)
        self.save()

    def set_waiting(self, request) -> None:
        self.move_to(self.STATE.WAITING)
        self.create_confirmation(request)
        self.save()
        if self.contract_procedure.auto_accept or (self.creditor == self.debitor):
            self.set_running(request)

    def set_running(self, request) -> None:
        self.move_to(self.STATE.RUNNING)
        if not self.contract_procedure.auto_accept:
            self.create_acceptance(request)
        if self.payment_method.is_prepayment:
            self.settle_claims()
        else:
            self.set_initial_settlement_log()
        self.save()

    def set_finalized(self) -> None:
        self.move_to(self.STATE.FINALIZED)
        self.save()

    def claim_factory(self):
        pass

    def settle_claims(self):
        from .jobs import notify
        now = timezone.now()
        selector = now + \
            timedelta(
                days=self.contract_procedure.settlement_interval
            ) if self.payment_method.is_prepayment else now
        open_claims = self.claim_set.filter(
            status=Claim.STATUS.OPEN, period_end__lte=selector)
        if open_claims:
            invoice = None
            with transaction.atomic():
                invoice = Invoice.build(self, open_claims)
                invoice.save()
                PaymentMethod.objects.get_subclass(
                    pk=self.payment_method.pk).settle(self, open_claims, invoice)
                open_claims.update(status=Claim.STATUS.CLOSED)
                notify(
                    self.creditor,
                    Notification.ACTION.CREATE,
                    '{} {}'.format(_('invoice'), invoice.number),
                    '',
                    self.debitor,
                    Notification.LEVEL.MEDIUM,
                    _('%(sender)s has created a new invoice. See the attached file.') % {
                        'sender': self.creditor.name},
                    [invoice.file.path],
                )
                if self.is_fixed_term:
                    if not self.claim_set.filter(status=Claim.STATUS.OPEN).exists():
                        self.set_finalized()
        self.settlement_logs.create()


class SettlementLog(BaseModel):
    contract = models.ForeignKey(
        Contract,
        on_delete=models.CASCADE,
        related_name='settlement_logs',
    )
    timestamp = models.DateTimeField(
        default=timezone.now
    )


class Claim(BaseModel):
    class STATUS:
        OPEN = 'o'
        CLOSED = 'c'

    STATI = [
        (STATUS.OPEN, _('open')),
        (STATUS.CLOSED, _('closed')),
    ]

    contract = models.ForeignKey(
        Contract,
        on_delete=models.PROTECT,
    )
    status = models.CharField(
        choices=STATI,
        max_length=3,
        default=STATUS.OPEN,
    )
    item = models.CharField(
        max_length=255,
    )
    quantity = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    unit = models.CharField(
        max_length=5,
    )
    price = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    currency = models.CharField(
        default='EUR',
        max_length=5,
    )
    net = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    discount = PercentField()
    discounted_net = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    tax_rate = PercentField(
        verbose_name=_('tax rate applied in percent'),
    )
    gross = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()


class Trigger(models.Model):
    condition = models.CharField(
        choices=Contract.STATES,
        max_length=2,
    )
    name = models.CharField(
        max_length=64,
    )
    comment = models.CharField(
        max_length=255,
        null=True,
        blank=True,
    )
    owner = models.ForeignKey(
        Actor,
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        abstract = True

    # attributes
    objects = InheritanceManager()

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
    fee_absolute = models.BooleanField(default=False)
    fee_value = models.DecimalField(
        decimal_places=3,
        max_digits=13,
        default=0,
    )
    fee_tax_rate = PercentField(
        verbose_name=_('tax rate applied to payement fee')
    )
    is_prepayment = models.BooleanField(
        default=False,
        help_text=_(
            'If activated, claims within the following settlement interval are charged in advance')
    )

    # methods
    def initialize(self, contract, request) -> HttpResponse:
        raise NotImplementedError()

    def settle(self, contract, claims, invoice) -> None:
        pass

    def apply_fee(self, net):
        if self.fee_absolute:
            return self.fee_value
        return float(net) * (float(self.fee_value)/100)

    def apply_fee_tax(self, net):
        return float(net) * (1 + (float(self.fee_tax_rate)/100))


class ContractProcedure(models.Model):
    SETTLEMENT_INTERVALS = [
        (7, _('weekly')),
        (14, _('biweekly')),
        (30, _('monthly')),
    ]

    name = models.CharField(
        max_length=64,
    )
    auto_accept = models.BooleanField(
        default=False
    )
    terms_and_conditions = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('terms and conditions'),
    )
    notes = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('notes'),
    )
    payment_methods = models.ManyToManyField(
        PaymentMethod,
        blank=False,
    )
    tax_rate = PercentField(
        verbose_name=_('tax rate applied in percent'),
    )
    settlement_interval = models.IntegerField(
        choices=SETTLEMENT_INTERVALS,
        default=SETTLEMENT_INTERVALS[0][0],
    )
    triggers = models.ManyToManyField(
        ContractTrigger,
        blank=True,
        related_name='procedure'
    )
    owner = models.ForeignKey(
        Actor,
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    # attributes
    objects = InheritanceManager()

    @property
    def type_name(self):
        raise NotImplementedError()

    # methods
    def __str__(self):
        return '{}: {}'.format(self.type_name, self.name)

    def apply_tax(self, net):
        return float(net) * (1 + (float(self.tax_rate)/100))


class Gallery(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
    )


class GalleryImage(models.Model):
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(
        null=False,
        blank=True,
        upload_to='images/',
    )
    thumbnail = ImageSpecField(
        source='image',
        processors=[
            ResizeToFill(300, 300),
        ],
        format='JPEG',
        options={
            'quality': 70,
        }
    )


def invoice_filename(instance, filename: str) -> str:
    secret = get_random_string(
        length=16, allowed_chars=string.ascii_letters + string.digits)
    return 'invoices/{cred}/{con}/{no}--{secret}.{ext}'.format(
        cred=instance.contract.creditor.slug, con=instance.contract.uuid,
        no=instance.number, secret=secret,
        ext=filename.split('.')[-1]
    )


def today():
    return timezone.now().date()


class Invoice(BaseModel):
    contract = models.ForeignKey(
        Contract, related_name='invoices', db_index=True, on_delete=models.CASCADE)
    prefix = models.CharField(max_length=160, db_index=True)
    invoice_no = models.CharField(max_length=19, db_index=True)
    full_invoice_no = models.CharField(max_length=190, db_index=True)
    is_cancellation = models.BooleanField(default=False)
    refers = models.ForeignKey(
        'Invoice', related_name='referred', null=True, blank=True, on_delete=models.CASCADE)
    invoice_from_name = models.CharField(max_length=190, null=True)
    invoice_from = models.TextField(null=True)
    invoice_from_postal_code = models.CharField(max_length=190, null=True)
    invoice_from_city = models.CharField(max_length=190, null=True)
    invoice_from_country = CountryField(null=True)
    invoice_from_tax_id = models.CharField(max_length=190, null=True)
    invoice_from_vat_id = models.CharField(max_length=190, null=True)
    invoice_to = models.TextField()
    invoice_to_company = models.TextField(null=True)
    invoice_to_name = models.TextField(null=True)
    invoice_to_street = models.TextField(null=True)
    invoice_to_postal_code = models.CharField(max_length=190, null=True)
    invoice_to_city = models.TextField(null=True)
    invoice_to_state = models.CharField(max_length=190, null=True)
    invoice_to_country = CountryField(null=True)
    invoice_to_vat_id = models.TextField(null=True)
    invoice_to_beneficiary = models.TextField(null=True)
    date = models.DateField(default=today)
    locale = models.CharField(max_length=50, default='de')
    introductory_text = models.TextField(blank=True)
    additional_text = models.TextField(blank=True)
    reverse_charge = models.BooleanField(default=False)
    payment_provider_text = models.TextField(blank=True)
    footer_text = models.TextField(blank=True)
    foreign_currency_display = models.CharField(
        max_length=50, null=True, blank=True)
    foreign_currency_rate = models.DecimalField(
        decimal_places=4, max_digits=10, null=True, blank=True)
    foreign_currency_rate_date = models.DateField(null=True, blank=True)
    shredded = models.BooleanField(default=False)

    file = models.FileField(null=True, blank=True,
                            upload_to=invoice_filename, max_length=255)
    internal_reference = models.TextField(blank=True)
    custom_field = models.CharField(max_length=255, null=True)

    @staticmethod
    def _to_numeric_invoice_number(number):
        return '{:05d}'.format(int(number))

    @property
    def full_invoice_from(self):
        taxidrow = ""
        if self.invoice_from_tax_id:
            if str(self.invoice_from_country) == "AU":
                taxidrow = "ABN: %s" % self.invoice_from_tax_id
            else:
                taxidrow = pgettext(
                    "invoice", "Tax ID: %s") % self.invoice_from_tax_id
        parts = [
            self.invoice_from_name,
            self.invoice_from,
            (self.invoice_from_postal_code or "") +
            " " + (self.invoice_from_city or ""),
            self.invoice_from_country.name if self.invoice_from_country else "",
            pgettext(
                "invoice", "VAT-ID: %s") % self.invoice_from_vat_id if self.invoice_from_vat_id else "",
            taxidrow,
            self.contract.creditor.telephone_public,
            self.contract.creditor.website,
        ]
        return '\n'.join([p.strip() for p in parts if p and p.strip()])

    @property
    def address_invoice_from(self):
        parts = [
            self.invoice_from_name,
            self.invoice_from,
            (self.invoice_from_postal_code or "") +
            " " + (self.invoice_from_city or ""),
            self.invoice_from_country,
        ]
        return '\n'.join([p.strip() for p in parts if p and p.strip()])

    @property
    def address_invoice_to(self):
        if self.invoice_to and not self.invoice_to_company and not self.invoice_to_name:
            return self.invoice_to

        state_name = ""
        if self.invoice_to_state:
            state_name = self.invoice_to_state
            if str(self.invoice_to_country) in COUNTRIES_WITH_STATE_IN_ADDRESS:
                if COUNTRIES_WITH_STATE_IN_ADDRESS[str(self.invoice_to_country)][1] == 'long':
                    state_name = pycountry.subdivisions.get(
                        code='{}-{}'.format(self.invoice_to_country,
                                            self.invoice_to_state)
                    ).name

        parts = [
            self.invoice_to_company,
            self.invoice_to_name,
            self.invoice_to_street,
            ((self.invoice_to_postal_code or "") + " " +
             (self.invoice_to_city or "") + " " + (state_name or "")).strip(),
            self.invoice_to_country.name if self.invoice_to_country else "",
        ]
        return '\n'.join([p.strip() for p in parts if p and p.strip()])

    def _get_numeric_invoice_number(self):
        numeric_invoices = Invoice.objects.filter(
            contract__creditor=self.contract.creditor,
            prefix=self.prefix,
        ).exclude(invoice_no__contains='-').annotate(
            numeric_number=Cast('invoice_no', models.IntegerField())
        ).aggregate(
            max=Max('numeric_number')
        )['max'] or 0
        return self._to_numeric_invoice_number(numeric_invoices + 1)

    def save(self, *args, **kwargs):
        if not self.contract:
            raise ValueError(
                'Every invoice needs to be connected to a contract')
        if not self.prefix:
            self.prefix = self.contract.creditor.invoice_numbers_prefix
            # if self.is_cancellation:
            #     self.prefix = self.contract.creditor.invoice_numbers_prefix_cancellations or self.prefix

        if not self.invoice_no:
            for i in range(10):
                self.invoice_no = self._get_numeric_invoice_number()
                try:
                    with transaction.atomic():
                        return super().save(*args, **kwargs)
                except DatabaseError:
                    # Suppress duplicate key errors and try again
                    if i == 9:
                        raise

        self.full_invoice_no = self.number
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """
        Deleting an Invoice would allow for the creation of another Invoice object
        with the same invoice_no as the deleted one. For various reasons, invoice_no
        should be reliably unique for an event.
        """
        raise Exception(
            'Invoices cannot be deleted, to guarantee uniqueness of Invoice.invoice_no in any event.')

    @property
    def number(self):
        """
        Returns the invoice number in a human-readable string with the event slug prepended.
        """
        return '{prefix}-{code}'.format(
            prefix=self.prefix,
            code=self.invoice_no
        )

    class Meta:
        unique_together = ('contract', 'prefix', 'invoice_no')
        ordering = ('date', 'invoice_no',)

    def __repr__(self):
        return '<Invoice {} / {}>'.format(self.full_invoice_no, self.pk)

    def create_pdf(self):
        if self.shredded:
            return None
        if self.file:
            self.file.delete()
        with language(self.locale):
            fname, ftype, fcontent = InvoiceRenderer().generate(self)
            self.file.save(fname, ContentFile(fcontent))
            self.save()
            return self.file.name

    @classmethod
    def build(cls, contract, claims):
        invoice = cls()
        invoice.contract = contract
        creditor = contract.creditor
        debitor = contract.debitor
        with language('en'):
            invoice.invoice_from = '{} {}'.format(
                creditor.address.street, creditor.address.street_number)
            invoice.invoice_from_name = creditor.name
            invoice.invoice_from_postal_code = creditor.address.postal_code
            invoice.invoice_from_city = creditor.address.city
            # invoice.invoice_from_country = creditor.address.country
            invoice.invoice_from_tax_id = creditor.tax_id
            invoice.invoice_from_vat_id = creditor.vat_id

            introductory = creditor.invoice_introductory_text
            additional = creditor.invoice_additional_text
            footer = creditor.invoice_footer_text

            invoice.introductory_text = str(
                introductory).replace('\n', '<br />')
            invoice.additional_text = str(additional).replace('\n', '<br />')
            invoice.footer_text = str(footer)
            # invoice.payment_provider_text = str(
            #     payment).replace('\n', '<br />')
            ia = debitor.address
            addr_template = pgettext("invoice", """
{name}
{i.street}
{i.postal_code} {i.city}""")
            # invoice.invoice_to = "\n".join(
            #     a.strip() for a in addr_template.format(
            #         i=ia,
            #         name=debitor.name,
            #     ).split("\n") if a.strip()
            # )
            invoice.invoice_to_name = debitor.name
            invoice.invoice_to_street = ia.street
            invoice.invoice_to_postal_code = ia.postal_code
            invoice.invoice_to_city = ia.city
            # invoice.invoice_to_country = ia.country

            if debitor.vat_id:
                invoice.invoice_to += "\n" + \
                    pgettext("invoice", "VAT-ID: %s") % debitor.vat_id
                invoice.invoice_to_vat_id = debitor.vat_id

            invoice.save()

            for i, c in enumerate(claims.order_by('-period_start')):
                InvoicePosition.objects.create(
                    position=i,
                    invoice=invoice,
                    item=c.item,
                    quantity=c.quantity,
                    unit=c.unit,
                    price=c.price,
                    currency=c.currency,
                    net=c.net,
                    discount=c.discount,
                    discounted_net=c.discounted_net,
                    tax_rate=c.tax_rate,
                    gross=c.gross,
                    period_start=c.period_start,
                    period_end=c.period_end,
                )

            invoice.create_pdf()
            return invoice


class InvoicePosition(models.Model):
    invoice = models.ForeignKey(
        'Invoice', related_name='positions', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    item = models.CharField(
        max_length=255,
    )
    quantity = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    unit = models.CharField(
        max_length=5,
    )
    price = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    currency = models.CharField(
        default='EUR',
        max_length=5,
    )
    net = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    discount = PercentField()
    discounted_net = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    tax_rate = PercentField(
        verbose_name=_('tax rate applied in percent'),
    )
    gross = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()

    @property
    def net_value(self):
        return self.gross - self.discounted_net

    class Meta:
        ordering = ('position', 'pk')

    def __str__(self):
        return 'Line {} of invoice {}'.format(self.position, self.invoice)
