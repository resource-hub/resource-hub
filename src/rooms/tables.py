import django_tables2 as tables
from django_tables2.utils import Accessor as A
from django.utils.translation import ugettext_lazy as _


class RoomsTable(tables.Table):
    name = tables.LinkColumn(
        # TODO make this
        'rooms:rooms_profile',
        verbose_name=_('Name'),
        kwargs={
            'organization_id': A('organization_id'),
        }
    )

    class Meta:
        attrs = {
            "class": "ui selectable celled table"
        }
