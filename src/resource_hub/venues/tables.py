from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import Accessor as A
from resource_hub.core.tables import SelectableTable


class VenuesTable(SelectableTable):
    name = tables.LinkColumn(
        'control:venues_edit',
        verbose_name=_('Name'),
        kwargs={
            'pk': A('pk'),
        }
    )
    owner = tables.Column(verbose_name=_('Owner'))

    class Meta(SelectableTable.Meta):
        pass
