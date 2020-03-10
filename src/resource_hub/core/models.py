from datetime import datetime, timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from ipware import get_client_ip
from model_utils.fields import MonitorField
from model_utils.managers import InheritanceManager


class Actor(models.Model):
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

    def save(self, *args, **kwargs):
        if not self.id:
            # Newly created object, so set slug
            self.slug = slugify(self.username)

        super(User, self).save(*args, **kwargs)


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
        if not self.id:
            self.slug = slugify(self.name)

        super(Location, self).save(*args, **kwargs)


class Organization(Actor):
    """
    juristic person
    """

    # fields
    members = models.ManyToManyField(
        User,
        through='OrganizationMember',
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    created_by = models.ForeignKey(
        User,
        related_name='organization_created_by',
        null=True,
        on_delete=models.SET_NULL,
    )

    # Methods
    def __str__(self):
        return super().name

    def save(self, *args, **kwargs):
        if not self.id:
            slug = slugify(self.name)
            try:
                Organization.objects.get(slug=slug)
                self.slug = slug + str(datetime.now().date())
            except Organization.DoesNotExist:
                self.slug = slug
        super(Organization, self).save(*args, **kwargs)


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
        default=None,
        on_delete=models.CASCADE
    )
    value = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    currency = models.CharField(
        default='EUR',
        max_length=5,
    )
    discounts = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return '{} {}'.format(
            self.value,
            self.currency
        )


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
    discount = models.IntegerField(
        default=0,
        validators=[
            MinValueValidator(0),
            MaxValueValidator(100),
        ]
    )

    # methods
    def __str__(self):
        addressee = '' if self.addressee is None else '({})'.format(
            self.addressee.name)
        return '{}%: {} {}'.format(self.discount, self.description, addressee)


class Claim(models.Model):
    item = models.CharField(max_length=255)
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
    tax_rate = models.IntegerField(
        default=0,
        verbose_name=_('tax rate applied in percent'),
    )
    net = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    gross = models.DecimalField(
        decimal_places=5,
        max_digits=15,
    )
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    created_at = models.DateTimeField(
        auto_now_add=True,
    )


class Contract(models.Model):
    # constants
    class STATE:
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
        (STATE.PENDING, _('pending')),
        (STATE.WAITING, _('waiting')),
        (STATE.RUNNING, _('running')),
        (STATE.DISPUTING, _('disputing')),
        (STATE.FINALIZED, _('finalized')),
        (STATE.EXPIRED, _('expired')),
        (STATE.CANCELED, _('canceled')),
        (STATE.DECLINED, _('declined')),
    ]

    # fields
    contract_procedure = models.ForeignKey(
        'ContractProcedure',
        on_delete=models.PROTECT,
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
    )
    state_changed = MonitorField(monitor='state')
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
    )
    claims = models.ManyToManyField(
        Claim,
        blank=True
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
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    created_by = models.ForeignKey(
        User,
        related_name='contract_created_by',
        null=True,
        on_delete=models.SET_NULL,
    )

    # attributes
    objects = InheritanceManager()

    @property
    def verbose_name(self) -> str:
        raise NotImplementedError()

    @property
    def is_pending(self) -> bool:
        return self.state is self.STATE.PENDING

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
        return ClaimTable(self.claims.all())

    # methods
    def call_triggers(self, state):
        return

    # state setters
    def move(self, state):
        self.call_triggers(state)
        self.state = state

    def set_pending(self, *args, **kwargs) -> None:
        self.move(self.STATE.PENDING)
        self.claim_factory(**kwargs)

    def set_expired(self) -> None:
        if self.state == self.STATE.PENDING:
            self.move(self.STATE.EXPIRED)
            self.save()
            return
        raise ValueError(
            'Cannot move from {} to state expired'.format(self.state))

    def set_canceled(self, request) -> None:
        if (self.state == self.STATE.PENDING):
            self.move(self.STATE.CANCELED)
            self.save()
            return
        raise ValueError(
            'Cannot move from {} to state canceled'.format(self.state))

    def set_declined(self, request) -> None:
        if self.STATE == self.STATE.WAITING:
            self.move(self.STATE.DECLINED)
            self.save()
        raise ValueError(
            'Cannot move from {} to state declined'.format(self.state))

    def set_waiting(self, request) -> None:
        if self.state == self.STATE.PENDING:
            self.move(self.STATE.WAITING)
            self.confirmation = DeclarationOfIntent.create(
                request=request,
            )
            self.save()

            if self.contract_procedure.auto_accept or (self.creditor == self.debitor):
                self.set_running(request)
            return
        raise ValueError(
            'Cannot move from {} to state waiting'.format(self.state))

    def set_running(self, request) -> None:
        if self.state == self.STATE.WAITING:
            self.move(self.STATE.RUNNING)
            self.acceptance = DeclarationOfIntent.create(
                request=request,
            )
            self.save()
            return
        raise ValueError(
            'Cannot move from {} to state waiting'.format(self.state))

    def claim_factory(self):
        raise NotImplementedError()


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

    @property
    def form_url(self) -> str:
        raise NotImplementedError()

    @property
    def edit_url(self, pk) -> str:
        raise NotImplementedError()

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

    # attributes
    @staticmethod
    def fixed_condtion() -> bool:
        return True

    @staticmethod
    def default_condition() -> str:
        return Contract.STATE.RUNNING

    @staticmethod
    def is_prepayment() -> bool:
        return False

    @staticmethod
    def redirect_route() -> str:
        return reverse('core:finance_payment_methods_add')


class ContractProcedure(models.Model):
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
        blank=True,
    )
    tax_rate = models.IntegerField(
        default=0,
        verbose_name=_('tax rate applied in percent'),
        validators=[
            MinValueValidator(0),
            MaxValueValidator(99),
        ]
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
