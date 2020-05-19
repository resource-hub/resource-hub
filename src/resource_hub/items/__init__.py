
from django.apps import AppConfig


class ItemsConfig(AppConfig):
    name = 'resource_hub.items'

    def ready(self):
        # register default options
        from resource_hub.venues.models import EventCategory, EventTag
        from . import signals


default_app_config = 'resource_hub.items.ItemsConfig'
