import django_tables2 as tables
from django_tables2.utils import Accessor as A
from django.utils.safestring import mark_safe as safe
from django.utils.translation import ugettext_lazy as _


class OrganizationsTable(tables.Table):
    name = tables.LinkColumn(
        'core:organizations_profile',
        verbose_name=_('Name'),
        kwargs={
            'organization_id': A('organization_id'),
        }
    )
    role = tables.Column(verbose_name=_('Your role'))
    # members = tables.LinkColumn(
    #     'core:organizations_members',
    #     text=safe('<i class="users icon"></i>'),
    #     verbose_name=_('Members'),
    #     kwargs={
    #         'id': A('profile'),
    #     }
    # )

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
