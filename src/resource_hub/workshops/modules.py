import os

from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _
from resource_hub.core.modules import BaseModule


class WorkshopsModule(BaseModule):
    @property
    def verbose_name(self):
        return _('Workshops')

    def get_navbar_items(self, request):
        return [
            {
                'header': _('Workshops'),
                'url': reverse('workshops:index'),
            },
        ]

    def get_sidebar_modules(self, request):
        first_child = reverse('control:workshops_manage')
        root = os.path.dirname(os.path.dirname(first_child))
        return [
            {
                'header': _('Workshops'),
                'url': root,
                'sub_items': [
                    {
                        'header': _('Manage'),
                        'url': first_child,
                    },
                    {
                        'header': _('Create'),
                        'url': reverse('control:workshops_create'),
                    },
                ]
            },
        ]

    def get_location_profile_item(self, context):
        return render_to_string(template_name='workshops/location_profile.html', context=context.flatten(), request=context.request)
