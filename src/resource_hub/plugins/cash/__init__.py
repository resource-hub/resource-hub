from django.apps import AppConfig


class CashConfig(AppConfig):
    name = 'resource_hub.plugins.cash'

    def ready(self):
        from . import signals


default_app_config = 'resource_hub.plugins.cash.CashConfig'
