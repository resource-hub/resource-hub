from django.apps import AppConfig


class BankTransfer(AppConfig):
    name = 'plugins.bank_transfer'

    def ready(self):
        from . import signals
