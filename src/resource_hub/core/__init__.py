from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = 'resource_hub.core'


default_app_config = 'resource_hub.core.CoreConfig'
