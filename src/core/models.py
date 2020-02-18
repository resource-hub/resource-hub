import string
from decimal import Decimal

from django.contrib.auth.models import AbstractUser
from django.db import DatabaseError, models, transaction
from django.db.models import Max
from django.db.models.functions import Cast
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.functional import cached_property
from django.utils.translation import pgettext
from django.utils.translation import ugettext_lazy as _

import pycountry
from core.settings import COUNTRIES_WITH_STATE_IN_ADDRESS
from django_countries.fields import CountryField
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill


class Actor(models.Model):
    # Fields
    name = models.CharField(
        max_length=128,
        null=True,
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

    @staticmethod
    def get_default():
        Actor.objects.get_or_create(pk=1)


class User(AbstractUser, Actor):
    """natural person."""
    email = models.EmailField(
        unique=True,
    )
    birth_date = models.DateField(
        null=True,
    )


class Address(models.Model):
    """describe address."""

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
    """describes a bank account."""

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
    """describing locations."""

    # Fields
    address = models.ForeignKey(
        Address,
        on_delete=models.CASCADE
    )
    name = models.CharField(
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


class Organization(Actor):
    """juristic person."""

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
    STATE_EXPIRED = 'x'
    STATE_CANCELED = 'c'

    STATES = [
        (STATE_PENDING, _('pending')),
        (STATE_CONFIRMED, _('confirmed')),
        (STATE_ACCEPTED, _('accepted')),
        (STATE_FINALIZED, _('finalized')),
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
    # fields
    function_call = models.CharField(
        max_length=128,
    )
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


class ContractTrigger(Trigger):
    provider = models.CharField(
        max_length=64,
    )


class Fee(models.Model):
    absolute = models.BooleanField(default=False)
    value = models.DecimalField(
        decimal_places=3,
        max_digits=13,
    )


class PaymentMethod(Trigger):
    fee = models.ForeignKey(
        Fee,
        on_delete=models.PROTECT,
    )


class BaseContractProcedure(models.Model):
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
        null=False,
        blank=True,
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


def invoice_filename(instance, filename: str) -> str:
    secret = get_random_string(
        length=16, allowed_chars=string.ascii_letters + string.digits)
    return 'invoices/{org}/{ev}/{no}-{code}-{secret}.{ext}'.format(
        org=instance.event.organizer.slug, ev=instance.event.slug,
        no=instance.number, code=instance.order.code, secret=secret,
        ext=filename.split('.')[-1]
    )


def today():
    return timezone.now().date()


class Invoice(models.Model):
    """Represents an invoice that is issued because of an order. Because
    invoices are legally required not to change, this object duplicates a lot
    of data (e.g. the invoice address).

    :param order: The associated order
    :type order: Order
    :param event: The event this belongs to (for convenience)
    :param event: The event this belongs to (for convenience)
    :param event: The event this belongs to (for convenience)
    :type event: Event
    :param organizer: The organizer this belongs to (redundant, for enforcing uniqueness)
    :type organizer: Organizer
    :param invoice_no: The human-readable, event-unique invoice number
    :type invoice_no: int
    :param is_cancellation: Whether or not this is a cancellation instead of an invoice
    :type is_cancellation: bool
    :param refers: A link to another invoice this invoice refers to, e.g. the canceled invoice in a cancellation
    :type refers: Invoice
    :param invoice_from: The sender address
    :type invoice_from: str
    :param invoice_to: The receiver address
    :type invoice_to: str
    :param full_invoice_no: The full invoice number (for performance reasons only)
    :type full_invoice_no: str
    :param date: The invoice date
    :type date: date
    :param locale: The locale in which the invoice should be printed
    :type locale: str
    :param introductory_text: Introductory text for the invoice, e.g. for a greeting
    :type introductory_text: str
    :param additional_text: Additional text for the invoice
    :type additional_text: str
    :param payment_provider_text: A payment provider specific text
    :type payment_provider_text: str
    :param footer_text: A footer text, displayed smaller and centered on every page
    :type footer_text: str
    :param foreign_currency_display: A different currency that taxes should also be displayed in.
    :type foreign_currency_display: str
    :param foreign_currency_rate: The rate of a foreign currency that the taxes should be displayed in.
    :type foreign_currency_rate: Decimal
    :param foreign_currency_rate_date: The date of the foreign currency exchange rates.
    :type foreign_currency_rate_date: date
    :param file: The filename of the rendered invoice
    :type file: File
    """
    contract = models.ForeignKey(
        Contract,
        on_delete=models.PROTECT
    )
    prefix = models.CharField(max_length=160, db_index=True)
    invoice_no = models.CharField(max_length=19, db_index=True)
    full_invoice_no = models.CharField(max_length=190, db_index=True)
    is_cancellation = models.BooleanField(default=False)
    refers = models.ForeignKey(
        'Invoice', related_name='refered', null=True, blank=True, on_delete=models.CASCADE)
    invoice_from = models.TextField()
    invoice_from_name = models.CharField(max_length=190, null=True)
    invoice_from_zipcode = models.CharField(max_length=190, null=True)
    invoice_from_city = models.CharField(max_length=190, null=True)
    invoice_from_country = CountryField(null=True)
    invoice_from_tax_id = models.CharField(max_length=190, null=True)
    invoice_from_vat_id = models.CharField(max_length=190, null=True)
    invoice_to = models.TextField()
    invoice_to_company = models.TextField(null=True)
    invoice_to_name = models.TextField(null=True)
    invoice_to_street = models.TextField(null=True)
    invoice_to_zipcode = models.CharField(max_length=190, null=True)
    invoice_to_city = models.TextField(null=True)
    invoice_to_state = models.CharField(max_length=190, null=True)
    invoice_to_country = CountryField(null=True)
    invoice_to_vat_id = models.TextField(null=True)
    invoice_to_beneficiary = models.TextField(null=True)
    date = models.DateField(default=today)
    locale = models.CharField(max_length=50, default='en')
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

    @staticmethod
    def _to_numeric_invoice_number(number):
        return '{:05d}'.format(int(number))

    @property
    def full_invoice_from(self):
        parts = [
            self.invoice_from_name,
            self.invoice_from,
            (self.invoice_from_zipcode or "") +
            " " + (self.invoice_from_city or ""),
            self.invoice_from_country.name if self.invoice_from_country else "",
            pgettext(
                "invoice", "VAT-ID: %s") % self.invoice_from_vat_id if self.invoice_from_vat_id else "",
            pgettext(
                "invoice", "Tax ID: %s") % self.invoice_from_tax_id if self.invoice_from_tax_id else "",
        ]
        return '\n'.join([p.strip() for p in parts if p and p.strip()])

    @property
    def address_invoice_from(self):
        parts = [
            self.invoice_from_name,
            self.invoice_from,
            (self.invoice_from_zipcode or "") +
            " " + (self.invoice_from_city or ""),
            self.invoice_from_country.name if self.invoice_from_country else "",
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
            ((self.invoice_to_zipcode or "") + " " +
             (self.invoice_to_city or "") + " " + (state_name or "")).strip(),
            self.invoice_to_country.name if self.invoice_to_country else "",
        ]
        return '\n'.join([p.strip() for p in parts if p and p.strip()])

    # def _get_numeric_invoice_number(self):
    #     numeric_invoices = Invoice.objects.filter(
    #         event__organizer=self.event.organizer,
    #         prefix=self.prefix,
    #     ).exclude(invoice_no__contains='-').annotate(
    #         numeric_number=Cast('invoice_no', models.IntegerField())
    #     ).aggregate(
    #         max=Max('numeric_number')
    #     )['max'] or 0
    #     return self._to_numeric_invoice_number(numeric_invoices + 1)

    # def _get_invoice_number_from_order(self):
    #     return '{order}-{count}'.format(
    #         order=self.contract.uuid,
    #         count=Invoice.objects.filter(
    #             event=self.event, order=self.order).count() + 1,
    #     )

    # def save(self, *args, **kwargs):
    #     if not self.contract:
    #         raise ValueError('Every invoice needs to be connected to an order')
    #     if not self.prefix:
    #         self.prefix = self.event.settings.invoice_numbers_prefix or (
    #             self.event.slug.upper() + '-')
    #         if self.is_cancellation:
    #             self.prefix = self.event.settings.invoice_numbers_prefix_cancellations or self.prefix
    #         if '%' in self.prefix:
    #             self.prefix = self.date.strftime(self.prefix)

    #     if not self.invoice_no:
    #         for i in range(10):
    #             self.invoice_no = self._get_invoice_number_from_order()
    #             try:
    #                 with transaction.atomic():
    #                     return super().save(*args, **kwargs)
    #             except DatabaseError:
    #                 # Suppress duplicate key errors and try again
    #                 if i == 9:
    #                     raise

    #     self.full_invoice_no = self.prefix + self.invoice_no
    #     return super().save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     """
    #     Deleting an Invoice would allow for the creation of another Invoice object
    #     with the same invoice_no as the deleted one. For various reasons, invoice_no
    #     should be reliably unique for an event.
    #     """
    #     raise Exception(
    #         'Invoices cannot be deleted, to guarantee uniqueness of Invoice.invoice_no in any event.')

    # @property
    # def number(self):
    #     """
    #     Returns the invoice number in a human-readable string with the event slug prepended.
    #     """
    #     return '{prefix}{code}'.format(
    #         prefix=self.prefix,
    #         code=self.invoice_no
    #     )

    # @cached_property
    # def canceled(self):
    #     return self.refered.filter(is_cancellation=True).exists()

    # class Meta:
    #     unique_together = ('organizer', 'prefix', 'invoice_no')
    #     ordering = ('date', 'invoice_no',)

    # def __repr__(self):


class InvoiceLine(models.Model):
    """One position listed on an Invoice.

    :param invoice: The invoice this belongs to
    :type invoice: Invoice
    :param description: The item description
    :param description: The item description
    :param description: The item description
    :param gross_value: The gross value
    :type gross_value: decimal.Decimal
    :param tax_value: The included tax (as an absolute value)
    :type tax_value: decimal.Decimal
    :param tax_rate: The applied tax rate in percent
    :type tax_rate: decimal.Decimal
    :param tax_name: The name of the applied tax rate
    :type tax_name: str
    :param subevent: The subevent this line refers to
    :type subevent: SubEvent
    :param event_date_from: Event date of the (sub)event at the time the invoice was created
    :type event_date_from: datetime
    """
    invoice = models.ForeignKey(
        'Invoice', related_name='lines', on_delete=models.CASCADE)
    position = models.PositiveIntegerField(default=0)
    description = models.TextField()
    gross_value = models.DecimalField(max_digits=10, decimal_places=2)
    tax_value = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'))
    tax_rate = models.DecimalField(
        max_digits=7, decimal_places=2, default=Decimal('0.00'))
    tax_name = models.CharField(max_length=190)

    @property
    def net_value(self):
        return self.gross_value - self.tax_value

    class Meta:
        ordering = ('position', 'pk')

    def __str__(self):
        return 'Line {} of invoice {}'.format(self.position, self.invoice)
