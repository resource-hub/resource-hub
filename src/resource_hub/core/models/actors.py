from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from model_utils.managers import InheritanceManager

from ..utils import get_valid_slug
from .base import BaseModel


class Actor(BaseModel):
    # Fields
    name = models.CharField(
        max_length=128,
        null=True,
        verbose_name=_('Name'),
    )
    slug = models.SlugField(
        unique=True,
        db_index=True,
        max_length=50,
        verbose_name=_('Slug'),
    )
    address = models.OneToOneField(
        'Address',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Address'),
    )
    bank_account = models.OneToOneField(
        'BankAccount',
        null=True,
        on_delete=models.SET_NULL,
        verbose_name=_('Bank account'),
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='images/',
        default='images/default.png',
        verbose_name=_('Thumbnail'),
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
        },
    )
    thumbnail_large = ImageSpecField(
        source='image',
        processors=[
            ResizeToFill(300, 300),
        ],
        format='PNG',
        options={
            'quality': 90,
        },
    )
    telephone_private = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_('Telephone (private)'),
    )
    telephone_public = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        verbose_name=_('Telephone (public)'),
    )
    email_public = models.EmailField(
        null=True,
        blank=True,
        verbose_name=_('Email (public)'),
    )
    website = models.URLField(
        null=True,
        blank=True,
        verbose_name=_('Website'),
    )
    info_text = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Info text'),
    )
    # setting fields
    tax_id = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name=_('Tax-ID'),
    )
    vat_id = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name=_('VAT-ID'),
    )
    invoice_numbers_prefix = models.CharField(
        max_length=5,
        default='RH',
        verbose_name=_('Invoice numbers prefix'),
    )
    invoice_numbers_prefix_cancellations = models.CharField(
        max_length=5,
        default='CAN',
        verbose_name=_('Invoice numbers prefix (cancellations)'),
    )
    invoice_introductory_text = models.TextField(
        null=True,
        blank=True,
        default='',
        verbose_name=_('Invoice introductory text'),
    )
    invoice_additional_text = models.TextField(
        null=True,
        blank=True,
        default='',
        verbose_name=_('Invoice additional text'),
    )
    invoice_footer_text = models.TextField(
        null=True,
        blank=True,
        default='',
        verbose_name=_('Invoice footer text'),
    )
    invoice_logo_image = models.ImageField(
        null=True,
        blank=True,
        upload_to='images/',
        default='images/logo.png',
        verbose_name=_('Invoice logo image'),
    )

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
        verbose_name=_('Email'),
    )
    birth_date = models.DateField(
        null=True,
        verbose_name=_('Birth date'),
    )
    is_verified = models.BooleanField(
        default=False,
        blank=True,
        verbose_name=_('Verified?'),
    )

    @property
    def notification_recipients(self) -> list:
        return [self.email, ]

    def save(self, *args, **kwargs):
        if not self.pk:
            self.slug = get_valid_slug(Actor(), self.username)
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
            self.slug = get_valid_slug(Actor(), self.name)
        super(Organization, self).save(*args, **kwargs)


class OrganizationMember(BaseModel):
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
        verbose_name=_('Organization'),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name=_('User'),
    )
    role = models.IntegerField(
        choices=ORGANIZATION_ROLES,
        default=MEMBER,
        null=False,
        verbose_name=_('Role'),
    )

    class Meta:
        unique_together = ('organization', 'user',)

    def is_admin(self) -> bool:
        return self.role == OrganizationMember.ADMIN or self.role == OrganizationMember.OWNER

    @staticmethod
    def role_display_reverse(val: int) -> str:
        for item in OrganizationMember.ORGANIZATION_ROLES:
            if item[0] == val:
                return item[1]
        raise ValueError('Corresponding role does not exist')

    @staticmethod
    def get_role(user, organization) -> str:
        return OrganizationMember.objects.get(
            organization=organization,
            user=user
        )
