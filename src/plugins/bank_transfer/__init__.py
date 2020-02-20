from django.apps import AppConfig


class BankTransferConfig(AppConfig):
    name = 'plugins.bank_transfer'

    def ready(self):
        from . import signals
        from .urls import register_urls
        register_urls()


default_app_config = 'plugins.bank_transfer.BankTransferConfig'
