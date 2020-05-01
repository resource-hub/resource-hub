from django.forms import HiddenInput, Select
from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import Accessor as A

from .forms import OrganizationMember


class BoolColumn(tables.Column):
    def render(self, record, value):
        if value:
            return mark_safe('<i class="large green checkmark icon"></i>')
        return ''


class PaymentMethodsTable(tables.Table):
    name = tables.Column(
        linkify=('control:finance_payment_methods_edit', {'pk': A('pk')}))
    verbose_name = tables.Column(verbose_name=_('Type'))
    is_prepayment = BoolColumn(
        verbose_name=_('Prepayment'),
    )
    owner = tables.Column(verbose_name=_('Owner'))

    class Meta:
        attrs = {
            "class": "ui selectable celled table"
        }


class OrganizationsTable(tables.Table):
    name = tables.Column(
        verbose_name=_('Name'),
        linkify=(
            'control:organizations_profile',
            {
                'organization_id': A('id'),
            }
        ),
    )
    role = tables.Column(verbose_name=_('Rights'))

    def render_role(self, value):
        return OrganizationMember.role_display_reverse(value)

    class Meta:
        attrs = {
            "class": "ui selectable celled table"
        }


class MembersTable(tables.Table):
    username = tables.Column(verbose_name=_(
        'Username'), accessor=A('user__username'))
    first_name = tables.Column(verbose_name=_('First name'),
                               accessor=A('user__first_name'))
    last_name = tables.Column(verbose_name=_('Last name'),
                              accessor=A('user__last_name'))
    role = tables.Column(verbose_name=_('Organization Role'))

    def render_role(self, value, record):
        widget = Select(
            attrs={'class': 'input select-dropdown'},
            choices=OrganizationMember.ORGANIZATION_ROLES)
        return widget.render('role', record.role)

    class Meta:
        attrs = {
            "class": "ui selectable celled table",
        }

        row_attrs = {
            "class": "row",
            "pk": lambda record: A('pk').resolve(record),
        }


class LocationsTable(tables.Table):
    name = tables.LinkColumn(
        'control:locations_profile_edit',
        verbose_name=_('Name'),
        kwargs={
            'pk': A('id'),
        }
    )
    owner = tables.Column()

    class Meta:
        attrs = {
            "class": "ui selectable celled table"
        }


def create_footer(table):
    if table.data:
        return table.data[0].currency


class ClaimTable(tables.Table):
    # columns
    item = tables.Column(verbose_name=_('Item'))
    period_start = tables.Column(verbose_name=_('Performance period start'))
    period_end = tables.Column(verbose_name=_('Performance period end'))
    quantity = tables.Column(verbose_name=_('Quantity'))
    unit = tables.Column(verbose_name=_('Unit'))
    price = tables.Column(verbose_name=_('Price/unit'))
    net = tables.Column(verbose_name=_('Net'))
    discount = tables.Column(verbose_name=_('Discount (%)'))
    discounted_net = tables.Column(verbose_name=_('Discounted net'))
    tax_rate = tables.Column(verbose_name=_('Tax (%)'))
    gross = tables.Column(verbose_name=_(
        'Gross'), footer=lambda table: sum(x.gross for x in table.data))
    currency = tables.Column(verbose_name=_(
        'Currency'), footer=create_footer)

    class Meta:
        attrs = {
            "class": "ui selectable table"
        }
        pagination = {
            'class': 'ui'
        }


class ContractProcedureTable(tables.Table):
    # columns
    pk = tables.Column(verbose_name=_('Type'))
    owner = tables.Column(verbose_name=_('Owner'))

    def render_pk(self, value, record):
        return mark_safe('<a href="{}">{}</a>'.format(record.edit_link, record.type_name))

    class Meta:
        attrs = {
            "class": "ui selectable table"
        }


class InvoiceTable(tables.Table):
    pk = tables.Column(verbose_name=_('Invoice Number'))
    invoice_to_name = tables.Column(verbose_name=_('Invoice to'))
    invoice_from_name = tables.Column(verbose_name=_('Invoice from'))
    file = tables.Column(verbose_name=_('File'))
    created_at = tables.DateColumn(verbose_name=('Date'))

    def render_pk(self, value, record):
        return record.number

    def render_file(self, value, record):
        return mark_safe('<a href="{}"><i class="icon file"></i></a>'.format(value.url))

    class Meta:
        attrs = {
            "class": "ui selectable table"
        }
