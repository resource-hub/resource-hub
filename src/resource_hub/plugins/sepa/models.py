import string
import uuid
from collections import defaultdict
from decimal import Decimal

from django.contrib import messages
from django.core.files.base import ContentFile
from django.db import DatabaseError, models, transaction
from django.db.models import Max
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.translation import ugettext_lazy as _

from resource_hub.core.fields import CurrencyField
from resource_hub.core.models import (Actor, BankAccount, BaseModel, Contract,
                                      Notification, Payment, PaymentMethod)
from resource_hub.core.utils import round_decimal
from sepaxml import SepaDD


class SEPAMandate(Contract):
    @property
    def verbose_name(self):
        return _('SEPA Mandate')

    @property
    def overview(self):
        return render_to_string('sepa/_mandate.html')

    # state setters
    def set_pending(self):
        self.move_to(self.STATE.PENDING)
        self.save()

    def set_running(self, request):
        self.move_to(self.STATE.WAITING)
        self.create_confirmation(request)
        self.move_to(self.STATE.RUNNING)
        self.save()


class SEPA(PaymentMethod):
    # fields
    creditor_id = models.CharField(
        max_length=25,
        verbose_name=_('SEPA Creditor Identifier'),
    )
    bank_account = models.ForeignKey(
        BankAccount,
        on_delete=models.PROTECT,
    )

    # attributes
    @property
    def verbose_name(self) -> str:
        return _('SEPA Direct Debit')

    @property
    def info(self) -> dict:
        return {
            'name': SEPA.verbose_name,
            'provider': 'Resource Hub Team',
            'description': _('Creates the necessary mandate and XML files for SEPA DD payments'),
            'thumbnail': 'images/default.png',
        }

    @property
    def form(self):
        from .forms import SEPAForm
        return SEPAForm

    @property
    def prefix(self) -> str:
        return 'sepa'

    # methods
    def callback(self):
        return

    def initialize(self, contract, request):
        if SEPAMandate.objects.filter(
            creditor=contract.creditor,
            debitor=contract.debitor,
            state=SEPAMandate.STATE.RUNNING
        ).exists():
            contract.set_waiting(request)
            message = _('%(name)s has been confirmed successfully') % {
                'name': contract.verbose_name}
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_contracts_manage_details', kwargs={'pk': contract.pk}))
        with transaction.atomic():
            mandate = SEPAMandate.objects.create(
                creditor=contract.creditor,
                debitor=contract.debitor,
                state=Contract.STATE.PENDING,
            )
            mandate.terms_and_conditions = mandate.overview
            mandate.save()
        return redirect(
            reverse(
                'control:sepa_mandate',
                kwargs={
                    'contract_pk': contract.pk,
                    'mandate_pk': mandate.pk}
            )
        )

    def settle(self, contract, claims, invoice):
        currency_map = defaultdict(Decimal)
        for claim in claims:
            currency_map[claim.currency] += claim.gross
            if claim.contract != contract:
                raise ValueError(
                    'claims have to be related to the same contract')

        for currency, total in currency_map.items():
            description = '{}: {}'.format(
                contract.verbose_name, invoice.number) if invoice else contract.verbose_name
            mandate = SEPAMandate.objects.get(
                creditor=contract.creditor, debitor=contract.debitor, state=Contract.STATE.RUNNING)
            sepa_type = 'RCUR' if SEPADirectDebitPayment.objects.filter(
                debitor=contract.debitor, mandate=mandate).exists() else 'FRST'
            SEPADirectDebitPayment.objects.create(
                payment_method=self,
                state=SEPADirectDebitPayment.STATE.PENDING,
                creditor=contract.creditor,
                debitor=contract.debitor,
                value=total,
                name=contract.debitor.name,
                iban=contract.debitor.bank_account.iban,
                bic=contract.debitor.bank_account.bic,
                amount=100*round_decimal(total, currency=currency),
                currency=currency,
                sepa_type=sepa_type,
                mandate=mandate,
                description=description,
            )

    def get_invoice_text(self):
        return _('This invoice has been settled with SEPA Direct Debit')


def sepaxml_filename(instance, filename: str) -> str:
    secret = get_random_string(
        length=32, allowed_chars=string.ascii_letters + string.digits)
    return 'sepaxml/{cred}/{no}--{secret}.{ext}'.format(
        cred=instance.creditor.slug,
        no=instance.number, secret=secret,
        ext=filename.split('.')[-1]
    )


class SEPADirectDebitXML(BaseModel):
    creditor = models.ForeignKey(
        Actor,
        on_delete=models.PROTECT,
    )
    creditor_identifier = models.CharField(
        max_length=25,
    )
    xml_no = models.CharField(max_length=19, db_index=True)
    full_xml_no = models.CharField(max_length=190, db_index=True)
    collection_date = models.DateField()
    name = models.CharField(
        max_length=70,
    )
    iban = models.CharField(
        max_length=40,
    )
    bic = models.CharField(
        max_length=11,
    )
    batch = models.BooleanField(
        default=True,
        blank=True,
        verbose_name=_('Batch booking'),
    )
    currency = CurrencyField()
    file = models.FileField(upload_to=sepaxml_filename)
    @property
    def prefix(self):
        return 'SEPA-DD'

    @property
    def number(self):
        return '{prefix}-{no}'.format(
            prefix=self.prefix,
            no=self.xml_no,
        )

    def _get_xml_number(self):
        xml_number = SEPADirectDebitXML.objects.filter(
            creditor=self.creditor,
        ).aggregate(
            max=Max('xml_no')
        )['max'] or 0
        return xml_number + 1

    def save(self, *args, **kwargs):
        if not self.xml_no:
            for i in range(10):
                self.xml_no = self._get_xml_number()
                try:
                    with transaction.atomic():
                        return super().save(*args, **kwargs)
                except DatabaseError:
                    # Suppress duplicate key errors and try again
                    if i == 9:
                        raise

        self.full_xml_no = self.number
        return super().save(*args, **kwargs)

    def create_xml(self, payments):
        xml_file = SepaDD({
            "name": self.name,
            "IBAN": self.iban,
            "BIC": self.bic,
            "batch": self.batch,
            "creditor_id": self.creditor_identifier,
            "currency": self.currency,
            "instrument": "COR1",
        }, schema="pain.008.003.02", clean=True)

        for payment in payments:
            xml_file.add_payment(
                {
                    "name": payment.name,
                    "IBAN": payment.iban,
                    "BIC": payment.bic,
                    "amount": payment.amount,
                    "type": payment.sepa_type,
                    "collection_date": self.collection_date,
                    "mandate_id": str(payment.mandate.uuid).replace('-', ''),
                    "mandate_date": payment.mandate.confirmation.timestamp.date(),
                    "description": payment.description,
                    "endtoend_id": str(payment.endtoend_id).replace('-', ''),
                })
            payment.sepa_dd_file = self
            payment.state = SEPADirectDebitPayment.STATE.FINALIZED
            payment.paymenent_date = self.collection_date

            Notification.build(
                type_=Notification.TYPE.MONETARY,
                sender=payment.creditor,
                recipient=payment.debitor,
                header=_('SEPA Direct Debit initiated'),
                message=_(
                    '''{creditor} with the creditor identifier 
                    {creditor_id} is going to debit your account {iban} 
                    with an amount of {amount} {currency} on the  
                    {collection_date}. This transaction is based 
                    on the mandate with the reference {mandate_id}.'''.format(
                        creditor=payment.creditor.name,
                        creditor_id=self.creditor_identifier,
                        iban=payment.iban[:-6] + 'XXXXXX',
                        amount=payment.value,
                        currency=payment.currency,
                        collection_date=self.collection_date,
                        mandate_id=str(payment.mandate.uuid),
                    )),
                link='',
                level=Notification.LEVEL.MEDIUM,
                target=self,
            )
            payment.save()

        self.file.save('test.xml', ContentFile(
            xml_file.export(validate=True)))
        self.save()
        return xml_file


class SEPADirectDebitPayment(Payment):
    sepa_dd_file = models.ForeignKey(
        SEPADirectDebitXML,
        on_delete=models.PROTECT,
        null=True,
        related_name='payments',
    )
    endtoend_id = models.UUIDField(
        default=uuid.uuid1,
        editable=False,
    )
    name = models.CharField(
        max_length=70,
    )
    iban = models.CharField(
        max_length=40,
    )
    bic = models.CharField(
        max_length=11,
    )
    amount = models.IntegerField()
    sepa_type = models.CharField(
        max_length=4,
        default='RCUR'
    )
    collection_date = models.DateField(
        null=True,
    )
    mandate = models.ForeignKey(
        SEPAMandate,
        on_delete=models.PROTECT,
    )
    description = models.CharField(
        max_length=140,
    )
