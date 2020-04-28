from collections import defaultdict

from django.contrib import messages
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render, reverse
from django.utils.translation import gettext_lazy as _
from django.views import View

from resource_hub.core.models import Contract, PaymentMethod
from resource_hub.core.utils import money_filter
from resource_hub.core.views import TableView
from resource_hub.core.views.control import get_subobject_or_404

from .forms import SEPADirectDebitXMLForm
from .models import SEPADirectDebitPayment, SEPADirectDebitXML, SEPAMandate
from .tables import OpenPaymentsTable, SEPAXMLFileTable


class SEPAMandateDetails(View):
    def get(self, request, mandate_pk, contract_pk):
        mandate = get_subobject_or_404(SEPAMandate, pk=mandate_pk)
        contract = get_subobject_or_404(Contract, pk=contract_pk)
        context = {
            'contract': mandate,
        }
        return render(request, 'sepa/control/sepa_mandate.html', context)

    def post(self, request, mandate_pk, contract_pk):
        mandate = get_subobject_or_404(SEPAMandate, pk=mandate_pk)
        contract = get_subobject_or_404(Contract, pk=contract_pk)
        actor = request.actor

        choice = request.POST.get('choice', None)
        if mandate.debitor == actor:
            is_debitor = True
        elif mandate.creditor == actor:
            is_debitor = False
        else:
            return HttpResponseForbidden

        if is_debitor:
            if choice == 'cancel':
                with transaction.atomic():
                    mandate.set_cancelled()
                message = _('{} has been canceled'.format(
                    mandate.verbose_name))
            elif choice == 'confirm':
                with transaction.atomic():
                    mandate.set_running(request)
                    contract.set_waiting(request)
                message = _('{} has been confirmed'.format(
                    mandate.verbose_name))
            else:
                message = _('Invalid Choice')

        messages.add_message(request, messages.SUCCESS, message)
        return redirect(reverse('control:finance_contracts_manage_details', kwargs={'pk': contract_pk}))


class XMLFilesManage(TableView):
    header = _('SEPA Direct Debit XML files')

    def get_queryset(self, request):
        return SEPADirectDebitXML.objects.filter(creditor=self.request.actor)

    def get_table(self):
        return SEPAXMLFileTable


class XMLFilesCreate(View):
    def get(self, request):
        total = SEPADirectDebitPayment.objects.filter(
            creditor=self.request.actor,
            state=SEPADirectDebitPayment.STATE.PENDING,
        ).aggregate(total=Sum('amount'))['total']
        total = total / 100 if total else 0
        context = {
            'form': SEPADirectDebitXMLForm(),
            'total': money_filter(total),
        }
        return render(request, 'sepa/control/files_create.html', context)

    def post(self, request):
        open_payments = SEPADirectDebitPayment.objects.filter(
            creditor=self.request.actor,
            state=SEPADirectDebitPayment.STATE.PENDING,
        )
        xml_file_form = SEPADirectDebitXMLForm(request.POST)

        if xml_file_form.is_valid():
            payment_map = defaultdict(list)
            count = 0
            with transaction.atomic():
                for payment in open_payments:
                    payment_map[payment.payment_method.pk].append(payment)

                for method, payments in payment_map.items():
                    method = PaymentMethod.objects.get_subclass(
                        pk=payments[0].payment_method.pk)
                    count += 1
                    xml_file = xml_file_form.save(commit=False)
                    xml_file.creditor = self.request.actor
                    xml_file.creditor_identifier = method.creditor_id
                    xml_file.name = method.bank_account.account_holder
                    xml_file.iban = method.bank_account.iban
                    xml_file.bic = method.bank_account.bic
                    xml_file.save()
                    xml_file.create_xml(payments)
                message = _('Successfully created {count} XML file(s)'.format(
                    count=count
                ))
        messages.add_message(request, messages.SUCCESS, message)
        return redirect(reverse('control:finance_sepa_files_manage'))


class OpenPayments(TableView):
    header = _('Open SEPA Direct Debit payments')

    def get_queryset(self, request):
        return SEPADirectDebitPayment.objects.filter(
            creditor=self.request.actor,
            state=SEPADirectDebitPayment.STATE.PENDING,
        )

    def get_table(self):
        return OpenPaymentsTable
