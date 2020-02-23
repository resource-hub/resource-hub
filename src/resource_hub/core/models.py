import string
from collections import OrderedDict
from datetime import datetime
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import DatabaseError, IntegrityError, models, transaction
from django.db.models import Max
from django.db.models.functions import Cast
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.text import slugify
from django.utils.translation import pgettext
from django.utils.translation import ugettext_lazy as _

import pycountry
from django_countries.fields import CountryField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from model_utils.managers import InheritanceManager
from resource_hub.core.settings import COUNTRIES_WITH_STATE_IN_ADDRESS


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
        return '{} {} in {} {}'.format(
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
    STATE_CREATED = 'c'
    STATE_PENDING = 'p'
    STATE_FINALIZED = 'f'
    STATE_FAILED = 'fa'
    STATE_CANCELED = 'ca'
    STATE_REFUNDED = 'r'

    STATES = [
        (STATE_PENDING, _('pending')),
        (STATE_FINALIZED, _('finalized')),
        (STATE_FAILED, _('failed')),
        (STATE_CANCELED, _('canceled')),
        (STATE_REFUNDED, _('refunded')),
    ]

    # fields
    state = models.CharField(
        choices=STATES,
        max_length=2,
    )
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
    ip = models.GenericIPAddressField()
    timestamp = models.DateTimeField()


class Contract(models.Model):
    # constants
    STATE_PENDING = 'p'
    STATE_CONFIRMED = 'co'
    STATE_ACCEPTED = 'a'
    STATE_FINALIZED = 'f'
    STATE_DISPUTED = 'd'
    STATE_EXPIRED = 'x'
    STATE_CANCELED = 'c'

    STATES = [
        (STATE_PENDING, _('pending')),
        (STATE_CONFIRMED, _('confirmed')),
        (STATE_ACCEPTED, _('accepted')),
        (STATE_FINALIZED, _('finalized')),
        (STATE_DISPUTED, _('disputed')),
        (STATE_EXPIRED, _('expired')),
        (STATE_CANCELED, _('canceled')),
    ]

    # fields
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
    payment = models.ForeignKey(
        Payment,
        null=True,
        on_delete=models.SET_NULL,
    )
    initiation = models.OneToOneField(
        DeclarationOfIntent,
        null=True,
        on_delete=models.SET_NULL,
        related_name='contract_initiation',
    )
    acceptance = models.OneToOneField(
        DeclarationOfIntent,
        on_delete=models.SET_NULL,
        null=True,
        related_name='contract_acceptance',
    )


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
        return Contract.STATE_ACCEPTED


class PaymentMethod(Trigger):
    # fields
    fee_absolute = models.BooleanField(default=False)
    fee_value = models.DecimalField(
        decimal_places=3,
        max_digits=13,
    )

    # attributes
    @staticmethod
    def fixed_condtion() -> bool:
        return True

    @staticmethod
    def default_condition() -> str:
        return Contract.STATE_ACCEPTED

    @staticmethod
    def is_prepayment() -> bool:
        return False

    @staticmethod
    def redirect_route() -> str:
        return reverse('core:finance_payment_methods_add')


class BaseContractProcedure(models.Model):
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
        verbose_name=_('tax rate applied to prices'),
    )
    trigger = models.ManyToManyField(
        ContractTrigger,
        blank=True,
        related_name='procedure'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        abstract = True


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
