import os

from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from resource_hub.control import sidebar_module_renderer


def control_sidebar(context, *args, **kwargs):
    first_child = reverse('control:venues_manage')
    root = os.path.dirname(os.path.dirname(first_child))
    return sidebar_module_renderer(
        [
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
        ],
        request=context.request,
    )


def navigation_bar(context, *args, **kwargs):
    return render_to_string(template_name='venues/hooks/navigation_bar.html', request=context.request)


def location_profile(context, *args, **kwargs):
    from resource_hub.venues.models import Venue
    location_slug = context.request.resolver_match.kwargs['slug']
    if not Venue.objects.filter(location__slug=location_slug):
        return ""
    return render_to_string(template_name='venues/hooks/location_profile.html', context=context.flatten(), request=context.request)
