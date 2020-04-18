from django.utils.html import mark_safe
from django.utils.translation import gettext_lazy as _

import django_tables2 as tables


class SEPAXMLFileTable(tables.Table):
    pk = tables.Column(verbose_name=_('File ID'))
    file = tables.Column(verbose_name=_('File'))
    collection_date = tables.DateColumn(verbose_name=('Collection date'))
    created_at = tables.DateTimeColumn(verbose_name=('Created'))

    def render_pk(self, value, record):
        return record.number

    def render_file(self, value, record):
        return mark_safe('<a href="{}"><i class="icon file"></i></a>'.format(value.url))

    class Meta:
        attrs = {
            "class": "ui selectable table"
        }


class OpenPaymentsTable(tables.Table):
    debitor = tables.Column(verbose_name=_('Debitor'))
    amount = tables.Column(verbose_name=_('Amount'))
    currency = tables.Column(verbose_name=_('Currency'))
    created_at = tables.DateColumn(verbose_name=('Date'))

    def render_amount(self, value, record):
        return value / 100

    class Meta:
        attrs = {
            "class": "ui selectable table"
        }
