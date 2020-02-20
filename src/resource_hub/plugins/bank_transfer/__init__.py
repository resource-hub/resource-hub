from django.apps import AppConfig


class BankTransferConfig(AppConfig):
    name = 'resource_hub.plugins.bank_transfer'

    def ready(self):
        from . import signals
        from .urls import register_urls
        register_urls()


default_app_config = 'resource_hub.plugins.bank_transfer.BankTransferConfig'
