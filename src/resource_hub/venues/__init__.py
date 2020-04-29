
from django.apps import AppConfig
from django.db.utils import ProgrammingError

from resource_hub.core.hooks import hook
from resource_hub.venues.hook_listeners import location_profile


class VenuesConfig(AppConfig):
    name = 'resource_hub.venues'

    def ready(self):
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
