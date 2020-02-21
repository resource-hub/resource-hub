from django.apps import AppConfig


class BankTransferConfig(AppConfig):
    name = 'resource_hub.plugins.bank_transfer'

    def ready(self):
        from . import signals


default_app_config = 'resource_hub.plugins.bank_transfer.BankTransferConfig'
