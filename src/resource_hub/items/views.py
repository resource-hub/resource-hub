from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views import View

from resource_hub.core.decorators import owner_required
from resource_hub.core.views import TableView

from .forms import (ItemContractFormManager, ItemContractProcedureFormManager,
                    ItemForm, ItemFormManager)
from .models import Item, ItemBooking, ItemContractProcedure
from .tables import (ItemBookingsCreditedTable, ItemBookingsDebitedTable,
                     ItemsTable)

TTL = 60 * 5

# @cache_page(TTL)


def index(request):
    return render(request, 'items/index.html')
# Admin section


@method_decorator(login_required, name='dispatch')
class ItemsManage(TableView):
    header = _('Manage items')
    class_ = Item

    def get_filters(self, request):
        return {
            'owner': {
                'value': request.actor,
                'connector': Q.AND,
            }
        }

    def get_table(self):
        return ItemsTable


@method_decorator(login_required, name='dispatch')
class ItemBookingsCredited(TableView):
    header = _('Credited item bookings')
    class_ = ItemBooking
    actions = False

    def get_filters(self, request):
        return {
            'contract__creditor': {
                'value': request.actor,
                'connector': Q.AND,
            },
        }

    def get_table(self):
        return ItemBookingsCreditedTable


@method_decorator(login_required, name='dispatch')
class ItemBookingsDebited(TableView):
    header = _('Debited item bookings')
    class_ = ItemBooking
    actions = False

    def get_filters(self, request):
        return {
            'contract__debitor': {
                'value': request.actor,
                'connector': Q.AND,
            },
        }

    def get_table(self):
        return ItemBookingsDebitedTable


@method_decorator(login_required, name='dispatch')
class ItemsCreate(View):
    def get(self, request):
        item_form = ItemFormManager(request.user, request.actor)
        return render(request, 'items/control/items_create.html', item_form.get_forms())

    def post(self, request):
        item_form = ItemFormManager(
            request.user, request.actor, data=request.POST, files=request.FILES)

        if item_form.is_valid():
            with transaction.atomic():
                item_form.save()

            message = ('The item has been created')
            messages.add_message(request, messages.SUCCESS, message)
            route = 'control:items_create' if request.POST.get(
                'another', None) else 'control:items_manage'
            return redirect(reverse(route))
        return render(request, 'items/control/items_create.html', item_form.get_forms())


@method_decorator(login_required, name='dispatch')
@method_decorator(owner_required, name='dispatch')
class ItemsEdit(View):
    template_name = 'items/control/items_edit.html'

    @classmethod
    def get_resource(cls):
        return Item

    def get(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        item_form = ItemFormManager(request.user, request.actor, instance=item)
        context = item_form.get_forms()
        context['item'] = item
        return render(request, self.template_name, context)

    def post(self, request, pk):
        item = get_object_or_404(Item, pk=pk)
        item_form = ItemFormManager(
            request.user,
            request.actor,
            data=request.POST,
            files=request.FILES,
            instance=item,
        )

        if item_form.is_valid():
            item_form.save()
            message = _('The item has been updated')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:items_edit', kwargs={'pk': pk}))

        context = item_form.get_forms()
        context['item'] = item
        return render(request, self.template_name, context)


class ItemsDetails(View):
    def get(self, request, owner_slug, item_slug):
        item = get_object_or_404(
            Item, slug=item_slug, owner__slug=owner_slug)
        context = {'item': item}
        return render(request, 'items/item_details.html', context)


@method_decorator(login_required, name='dispatch')
class ItemBookingsCreate(View):
    template_name = 'items/item_bookings_create.html'

    def get(self, request, owner_slug, item_slug):
        item = get_object_or_404(
            Item, slug=item_slug, owner__slug=owner_slug)
        context = ItemContractFormManager(item, request).get_forms()
        context['item'] = item
        return render(request, self.template_name, context)

    def post(self, request, owner_slug, item_slug):
        item = get_object_or_404(
            Item, slug=item_slug, owner__slug=owner_slug)
        item_contract_form = ItemContractFormManager(item, request)
        if item_contract_form.is_valid():
            with transaction.atomic():
                item_contract = item_contract_form.save()
                item_contract.claim_factory()
            message = _(
                'The event has been created successfully. You can review it and either confirm or cancel.')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_contracts_manage_details', kwargs={'pk': item_contract.pk}))
        context = item_contract_form.get_forms()
        context['item'] = item
        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class ContractProceduresCreate(View):
    template_name = 'items/control/contract_procedures_create.html'

    def get(self, request):
        contract_procedure_form = ItemContractProcedureFormManager(request)
        return render(request, self.template_name, contract_procedure_form.get_forms())

    def post(self, request):
        contract_procedure_form = ItemContractProcedureFormManager(request)

        if contract_procedure_form.is_valid():
            contract_procedure_form.save()
            message = _(
                'The event contract procedure has been saved successfully')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_contract_procedures_manage'))
        return render(request, self.template_name, contract_procedure_form.get_forms())


@method_decorator(login_required, name='dispatch')
@method_decorator(owner_required, name='dispatch')
class ContractProceduresEdit(View):
    template_name = 'items/control/contract_procedures_edit.html'

    @classmethod
    def get_resource(cls):
        return ItemContractProcedure

    def get(self, request, pk):
        contract_procedure = get_object_or_404(ItemContractProcedure, pk=pk)
        contract_procedure_form = ItemContractProcedureFormManager(
            request, instance=contract_procedure)
        return render(request, self.template_name, contract_procedure_form.get_forms())

    def post(self, request, pk):
        contract_procedure = get_object_or_404(ItemContractProcedure, pk=pk)
        contract_procedure_form = ItemContractProcedureFormManager(
            request, instance=contract_procedure)

        if contract_procedure_form.is_valid():
            contract_procedure_form.save()

            message = _('The changes have been saved')
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(reverse('control:finance_contract_procedures_manage'))
        return render(request, self.template_name, contract_procedure_form.get_forms())
