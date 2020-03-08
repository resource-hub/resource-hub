from django.utils.translation import ugettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import Accessor as A


class PaymentMethodsTable(tables.Table):
    name = tables.Column(
        linkify=('control:finance_payment_methods_edit', {'pk': A('pk')}))
    method_type = tables.Column()
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
        from resource_hub.core.models import OrganizationMember
        return OrganizationMember.role_display_reverse(value)

    class Meta:
        attrs = {
            "class": "ui selectable celled table"
        }


class MembersTable(tables.Table):
    username = tables.Column(verbose_name=_('Username'))
    first_name = tables.Column(verbose_name=_('First name'))
    last_name = tables.Column(verbose_name=_('Last name'))
    role = tables.Column(verbose_name=_('Organization Role'))

    class Meta:
        attrs = {
            "class": "ui selectable celled table",
        }

        row_attrs = {
            "class": "user",
            "id": lambda record: record['id'],
        }


class LocationsTable(tables.Table):
    name = tables.LinkColumn(
        'control:locations_profile_edit',
        verbose_name=_('Name'),
        kwargs={
            'location_id': A('id'),
        }
    )
    owner = tables.Column()

    class Meta:
        attrs = {
            "class": "ui selectable celled table"
        }


class ClaimTable(tables.Table):
    # columns
    item = tables.Column(verbose_name=_('Item'))
    quantity = tables.Column(verbose_name=_('Quantity'))
    unit = tables.Column(verbose_name=_('Unit'))
    price = tables.Column(verbose_name=_('Price/unit'))
    currency = tables.Column(verbose_name=_('Currency'))
    tax_rate = tables.Column(verbose_name=_('Tax (%)'))
    net = tables.Column(verbose_name=_('Net'))
    gross = tables.Column(verbose_name=_(
        'Gross'), footer=lambda table: sum(x.gross for x in table.data))

    class Meta:
        attrs = {
            "class": "ui selectable table"
        }


class ContractProcedureTable(tables.Table):
    # columns
    name = tables.Column(verbose_name=_('Type'))
    owner = tables.Column(verbose_name=_('Owner'))

    def render_name(self, value, record):
        return record.type_name

    class Meta:
        attrs = {
            "class": "ui selectable table"
        }
