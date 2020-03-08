
from django.apps import AppConfig
from django.db.utils import ProgrammingError

from resource_hub.core.hooks import hook
from resource_hub.venues.hook_listeners import (control_sidebar,
                                                location_profile,
                                                navigation_bar)


class VenuesConfig(AppConfig):
    name = 'resource_hub.venues'

    def ready(self):
        hook.register('control_sidebar', control_sidebar)
        hook.register('navigation_bar', navigation_bar)
        hook.register('location_profile', location_profile)

        # register default options
        from resource_hub.venues.models import EventCategory, EventTag
        try:
            EventCategory.objects.get_or_create(name='Sport')
            EventTag.objects.get_or_create(name='wild')
        except ProgrammingError:
            pass

        from . import signals


default_app_config = 'resource_hub.venues.VenuesConfig'
