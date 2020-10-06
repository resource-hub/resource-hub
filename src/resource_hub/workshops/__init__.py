
from django.apps import AppConfig
from django.db.utils import ProgrammingError
from resource_hub.core.hooks import hook

# from resource_hub.venues.hook_listeners import location_profile


class WorkshopsConfig(AppConfig):
    name = 'resource_hub.workshops'

    def ready(self):
        # hook.register('location_profile', location_profile)

        # register default options
        from . import signals


default_app_config = 'resource_hub.workshops.WorkshopsConfig'
