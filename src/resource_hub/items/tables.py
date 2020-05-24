from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import Accessor as A
from resource_hub.core.tables import SelectableTable


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
