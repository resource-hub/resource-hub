
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_countries.fields import CountryField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
from model_utils.fields import MonitorField
from model_utils.managers import InheritanceManager

from ..managers import CombinedManager
from ..utils import get_valid_slug


class BaseModel(models.Model):
    # fields
    is_deleted = models.BooleanField(
        default=False,
        verbose_name=_('Deleted?'),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created at'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated at'),
    )
    objects = CombinedManager()
    all_objects = InheritanceManager()

    class Meta:
        abstract = True

    # methods
    def soft_delete(self):
        self.is_deleted = True
        self.save()

    def get_subclass(self):
        return self.__class__.objects.get_subclass(pk=self.pk)


class BaseStateMachine(BaseModel):
    class STATE:
        PENDING = 'p'

    STATES = [
        (STATE.PENDING, _('pending')),
    ]
    STATE_GRAPH = None

    state = models.CharField(
        max_length=2,
        default=STATE.PENDING,
        verbose_name=_('State'),
    )
    state_changed = MonitorField(
        monitor='state',
        verbose_name=_('State changed at'),
    )

    def get_state_display(self):
        for state in self.STATES:
            if state[0] == self.state:
                return state[1]

    # state setters
    def move_to(self, state):
        if self.state in self.STATE_GRAPH and state in self.STATE_GRAPH[self.state]:
            self.state = state
        else:
            raise ValueError('Cannot move from state {} to state {}'.format(
                self.get_state_display(), state))

    class Meta:
        abstract = True


class Address(BaseModel):
    """
    describe address
    """

    # Fields
    street = models.CharField(
        max_length=50,
        null=True,
        blank=False,
        verbose_name=_('Street'),
    )
    street_number = models.CharField(
        max_length=10,
        null=True,
        blank=False,
        verbose_name=_('Street number'),
    )
    postal_code = models.CharField(
        max_length=5,
        null=True,
        blank=False,
        verbose_name=_('Postal code'),
    )
    city = models.CharField(
        max_length=128,
        null=True,
        blank=False,
        verbose_name=_('City'),
    )
    country = CountryField(
        null=True,
        blank=True,
        default=settings.DEFAULT_COUNTRY,
        verbose_name=_('Country'),
    )
    updated_by = models.ForeignKey(
        'User',
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


class BankAccount(BaseModel):
    """
    describes a bank account
    """

    # Fields
    account_holder = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_('Account holder'),
    )
    iban = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name=_('IBAN'),
    )
    bic = models.CharField(
        max_length=11,
        null=True,
        blank=True,
        verbose_name=_('BIC'),
    )
    updated_by = models.ForeignKey(
        'User',
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


class Location(BaseModel):
    """
    describing locations
    """

    # Fields
    slug = models.SlugField(
        max_length=50,
        unique=True,
        db_index=True,
        verbose_name=_('Slug'),
    )
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE,
        verbose_name=_('Address'),
    )
    name = models.CharField(
        max_length=128,
        null=True,
        blank=True,
        verbose_name=_('Name'),
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Description'),
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        default=0,
        verbose_name=_('Latitude'),
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        default=0,
        verbose_name=_('Longitude'),
    )
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to='images/',
        default='images/default.png',
        verbose_name=_('Image'),
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
    is_public = models.BooleanField(
        default=True,
        verbose_name=_('Public?'),
        help_text=_(
            'Display the location in feeds and display full information'),
    )
    is_editable = models.BooleanField(
        default=False,
        verbose_name=_('Editable?'),
        help_text=_(
            'Allow other users to link information to this location'),
    )
    owner = models.ForeignKey(
        'Actor',
        on_delete=models.CASCADE,
        verbose_name=_('Owner'),
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


class Gallery(BaseModel):
    pass


class GalleryImage(BaseModel):
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.PROTECT,
        related_name='images',
        verbose_name=_('Gallery'),
    )
    caption = models.CharField(
        max_length=255,
        verbose_name=_('Caption'),
    )
    image = models.ImageField(
        null=False,
        upload_to='images/',
        verbose_name=_('Image'),
    )
    thumbnail = ImageSpecField(
        source='image',
        processors=[
            ResizeToFill(400, 400),
        ],
        format='JPEG',
        options={
            'quality': 90,
        }
    )
