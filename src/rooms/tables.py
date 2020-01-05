from django.utils.translation import ugettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import Accessor as A


class RoomsTable(tables.Table):
    name = tables.LinkColumn(
        'admin:rooms_profile_edit',
        verbose_name=_('Name'),
        kwargs={
            'room_id': A('room_id'),
        }
    )
    owner = tables.Column(verbose_name=_('Owner'))

    class Meta:
        attrs = {
            "class": "ui selectable celled table"
        }
