import string

from django.core.files.base import ContentFile
from django.db import DatabaseError, models, transaction
from django.db.models import Max
from django.db.models.functions import Cast
from django.shortcuts import reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import gettext_lazy as _
from django.utils.translation import pgettext

import pycountry
from django_countries.fields import CountryField

from ..fields import CurrencyField, PercentField
from ..renderer import InvoiceRenderer
from ..settings import COUNTRIES_WITH_STATE_IN_ADDRESS
from ..utils import language
from .base import BaseModel
from .notifications import Notification


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
    '''
    thanks to https://github.com/pretix/pretix/blob/master/src/pretix/base/models/invoices.py
    '''
    contract = models.ForeignKey(
        'Contract', related_name='invoices', db_index=True, on_delete=models.CASCADE)
    prefix = models.CharField(max_length=160, db_index=True)
    invoice_no = models.CharField(max_length=19, db_index=True)
    full_invoice_no = models.CharField(max_length=190, db_index=True)
    is_cancellation = models.BooleanField(default=False)
    refers = models.ForeignKey(
        'Invoice', related_name='referred', null=True, blank=True, on_delete=models.CASCADE)
    invoice_from = models.TextField(null=True)
    invoice_from_name = models.CharField(max_length=190, null=True)
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
            self.invoice_from_country.name,
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
            if self.is_cancellation:
                self.prefix = self.contract.creditor.invoice_numbers_prefix_cancellations or self.prefix

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
        Notification.build(
            type_=Notification.TYPE.MONETARY,
            sender=self.contract.creditor,
            recipient=self.contract.debitor,
            header=_('%(creditor)s created invoice %(no)s') % {
                'creditor': self.contract.creditor.name,
                'no': self.full_invoice_no,
            },
            message=_('%(creditor)s has created a new invoice. See the attached file.') % {
                'creditor': self.contract.creditor.name},
            link=reverse('control:finance_invoices_incoming'),
            level=Notification.LEVEL.MEDIUM,
            target=self,
            attachments=[self.file.path, ],
        )
        return self.file.name

    @classmethod
    def build(cls, contract, claims):
        invoice = cls()
        invoice.contract = contract
        creditor = contract.creditor
        debitor = contract.debitor
        with language(creditor.language):
            invoice.locale = creditor.language
            invoice.invoice_from = '{} {}'.format(
                creditor.address.street, creditor.address.street_number)
            invoice.invoice_from_name = creditor.name
            invoice.invoice_from_postal_code = creditor.address.postal_code
            invoice.invoice_from_city = creditor.address.city
            invoice.invoice_from_country = creditor.address.country
            invoice.invoice_from_tax_id = creditor.tax_id
            invoice.invoice_from_vat_id = creditor.vat_id

            introductory = creditor.invoice_introductory_text
            additional = creditor.invoice_additional_text
            footer = creditor.invoice_footer_text

            invoice.introductory_text = str(
                introductory).replace('\n', '<br />')
            invoice.additional_text = str(additional).replace('\n', '<br />')
            invoice.footer_text = str(footer)
            invoice.payment_provider_text = (contract.payment_method.get_subclass(
            ).get_invoice_text() + '\n\n').replace('\n', '<br />')
            ia = debitor.address
            addr_template = pgettext("invoice", """
{name}
{i.street}
{i.postal_code} {i.city}""")
            invoice.invoice_to = "\n".join(
                a.strip() for a in addr_template.format(
                    i=ia,
                    name=debitor.name,
                ).split("\n") if a.strip()
            )
            invoice.invoice_to_name = debitor.name
            invoice.invoice_to_street = ia.street
            invoice.invoice_to_postal_code = ia.postal_code
            invoice.invoice_to_city = ia.city
            invoice.invoice_to_country = ia.country

            if debitor.vat_id:
                invoice.invoice_to += "\n" + (
                    pgettext("invoice", "VAT-ID: %s") % debitor.vat_id)
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
    currency = CurrencyField()
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
