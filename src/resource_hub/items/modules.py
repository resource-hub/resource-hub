import os

from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from resource_hub.core.modules import BaseModule


class ItemsModule(BaseModule):
    @property
    def verbose_name(self):
        return _('Items')

    def get_navbar_items(self, request):
        return [
            {
                'header': _('Items'),
                'url': reverse('items:index'),
            },
        ]

    def get_sidebar_modules(self, request):
        first_child = reverse('control:items_manage')
        root = os.path.dirname(os.path.dirname(first_child))
        return [
            {
                'header': _('Items'),
                'url': root,
                'sub_items': [
                    {
                        'header': _('Manage'),
                        'url': first_child,
                    },
                    {
                        'header': _('Create'),
                        'url': reverse('control:items_create'),
                    },
                    {
                        'header': _('Bookings credited'),
                        'url': reverse('control:item_bookings_credited'),
                    },
                    {
                        'header': _('Bookings debited'),
                        'url': reverse('control:item_bookings_debited'),
                    },
                ]
            },
        ]
