from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import Accessor as A
from resource_hub.core.tables import BaseTable, SelectableTable


class ItemsTable(SelectableTable):
    name = tables.LinkColumn(
        'control:items_edit',
        verbose_name=_('Name'),
        kwargs={
            'pk': A('pk'),
        }
    )
    state = tables.Column(verbose_name=_('State'))
    location = tables.Column(verbose_name=_('Location'))

    def render_state(self, value, record):
        return record.get_state_display()

    class Meta(SelectableTable.Meta):
        pass


class ItemBookingsCreditedTable(BaseTable):
    contract = tables.Column(linkify=(
        'control:finance_contracts_manage_details', {'pk': A('contract__pk')}), verbose_name=_('Contract'), accessor=A('contract__pk'))
    item = tables.Column(accessor=A('item__name'), verbose_name=_('Item'))
    actor = tables.Column(accessor=A(
        'contract__debitor'), verbose_name=_('Debitor'), orderable=False)
    dtstart = tables.Column(verbose_name=_('Start'))
    dtend = tables.Column(verbose_name=_('End'))

    class Meta(BaseTable.Meta):
        pass


class ItemBookingsDebitedTable(ItemBookingsCreditedTable):
    actor = tables.Column(accessor=A(
        'contract__creditor'), verbose_name=_('Debitor'), orderable=False)

    class Meta(BaseTable.Meta):
        pass
