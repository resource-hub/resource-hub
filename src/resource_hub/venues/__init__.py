
from django.apps import AppConfig

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


default_app_config = 'resource_hub.venues.VenuesConfig'
