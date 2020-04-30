import os

from django.shortcuts import reverse
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _


def location_profile(context, *args, **kwargs):
    from resource_hub.venues.models import Venue
    location_slug = context.request.resolver_match.kwargs['slug']
    if not Venue.objects.filter(location__slug=location_slug):
        return ""
    return render_to_string(template_name='venues/hooks/location_profile.html', context=context.flatten(), request=context.request)
