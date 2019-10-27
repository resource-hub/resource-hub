import django_tables2 as tables
from django_tables2.utils import Accessor as A
from django.utils.safestring import mark_safe as safe
from django.utils.translation import ugettext_lazy as _


class OrganizationsTable(tables.Table):
    name = tables.Column(verbose_name=_('Name'))
    # edit = tables.Column(linkify=('core:organizations_profile', {
    #                      'id': tables.A('edit'), 'scope': 'profile'}))
    profile = tables.LinkColumn('core:organizations_profile',
                                text=safe('<i class="edit outline icon"></i>'),
                                verbose_name=_('Profile'),
                                kwargs={
                                    'id': A('profile'),
                                    'scope': 'info'
                                })
    members = tables.LinkColumn('core:organizations_members',
                                text=safe('<i class="users icon"></i>'),
                                verbose_name=_('Members'),
                                kwargs={
                                    'id': A('profile'),
                                })

    class Meta:
        attrs = {"class": "ui selectable celled table"}


class MembersTable(tables.Table):
    username = tables.Column(verbose_name=_('Username'))
    first_name = tables.Column(verbose_name=_('First name'))
    last_name = tables.Column(verbose_name=_('Last name'))
    role = tables.Column(verbose_name=_('Organization Role'))

    class Meta:
        attrs = {"class": "ui selectable celled table"}
