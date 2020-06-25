from django.apps import AppConfig

from resource_hub.core.hook_listeners import (control_sidebar,
                                              location_profile, navigation_bar)
from resource_hub.core.hooks import hook


class CoreConfig(AppConfig):
    name = 'resource_hub.core'

    def ready(self):
        hook.register('navigation_bar', navigation_bar)
        hook.register('control_sidebar', control_sidebar)
        hook.register('location_profile', location_profile)

        from . import signals


default_app_config = 'resource_hub.core.CoreConfig'
