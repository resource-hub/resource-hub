import os

from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from resource_hub.core.modules import BaseModule


class VenuesModule(BaseModule):
    @property
    def verbose_name(self):
        return _('Venues')

    def get_navbar_items(self, request):
        return [
            {
                'header': _('Venues'),
                'url': reverse('venues:index'),
            },
        ]

    def get_sidebar_modules(self, request):
        first_child = reverse('control:venues_manage')
        root = os.path.dirname(os.path.dirname(first_child))
        return [
            {
                'header': _('Venues'),
                'url': root,
                'sub_items': [
                    {
                        'header': _('Manage'),
                        'url': first_child,
                    },
                    {
                        'header': _('Create'),
                        'url': reverse('control:venues_create'),
                    },
                ]
            },
        ]

    def get_location_profile_item(self, context):
        from resource_hub.venues.models import Venue
        location_slug = context.request.resolver_match.kwargs['slug']
        if not Venue.objects.filter(location__slug=location_slug):
            return ""
        return render_to_string(template_name='venues/location_profile.html', context=context.flatten(), request=context.request)
