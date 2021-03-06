from django.dispatch import receiver

from resource_hub.core.signals import (register_contract_procedures,
                                       register_modules)

from .models import ItemContractProcedure
from .modules import ItemsModule


@receiver(register_contract_procedures)
def register_contract_procedure(sender, **kwargs):
    return ItemContractProcedure().__class__


@receiver(register_modules)
def register_module(sender, **kwargs):
    return ItemsModule
