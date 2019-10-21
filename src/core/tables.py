import django_tables2 as tables
from django_tables2.utils import Accessor as A
from django.utils.safestring import mark_safe as safe


class OrganizationsTable(tables.Table):
    name = tables.Column()
    # edit = tables.Column(linkify=('core:organizations_profile', {
    #                      'id': tables.A('edit'), 'scope': 'profile'}))
    profile = tables.LinkColumn('core:organizations_profile',
                                text=safe('<i class="edit outline icon"></i>'),
                                kwargs={
                                    'id': A('profile'),
                                    'scope': 'info'
                                })

    class Meta:
        attrs = {"class": "ui selectable celled table"}
