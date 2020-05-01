from django.utils.translation import gettext_lazy as _

import django_tables2 as tables
from django_tables2.utils import Accessor as A


class VenuesTable(tables.Table):
    name = tables.LinkColumn(
        'control:venues_profile_edit',
        verbose_name=_('Name'),
        kwargs={
            'pk': A('pk'),
        }
    )
    owner = tables.Column(verbose_name=_('Owner'))

    class Meta:
        attrs = {
            "class": "ui selectable celled table"
        }
