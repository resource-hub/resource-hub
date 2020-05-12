
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
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
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
    )
    state_changed = MonitorField(monitor='state')

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
    )
    street_number = models.CharField(
        max_length=10,
        null=True,
        blank=False,
    )
    postal_code = models.CharField(
        max_length=5,
        null=True,
        blank=False,
    )
    city = models.CharField(
        max_length=128,
        null=True,
        blank=False,
    )
    country = CountryField(
        null=True,
        blank=True,
        default=settings.DEFAULT_COUNTRY,
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
        'Actor',
        on_delete=models.CASCADE,
    )
    created_by = models.ForeignKey(
        'User',
        null=True,
        related_name='location_created_by',
        on_delete=models.SET_NULL,
    )
    updated_by = models.ForeignKey(
        'User',
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


class Gallery(BaseModel):
    pass


class GalleryImage(BaseModel):
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.PROTECT,
        related_name='images'
    )
    caption = models.CharField(
        max_length=255,
    )
    image = models.ImageField(
        null=False,
        upload_to='images/',
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
