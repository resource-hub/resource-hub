from django.apps import AppConfig


class SEPAConfig(AppConfig):
    name = 'resource_hub.plugins.sepa'

    def ready(self):
        from . import signals


default_app_config = 'resource_hub.plugins.sepa.SEPAConfig'
