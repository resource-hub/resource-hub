from django.dispatch import receiver
from resource_hub.core.signals import (register_contract_procedures,
                                       register_modules)

from .models import WorkshopContractProcedure
from .modules import WorkshopsModule


@receiver(register_contract_procedures)
def register_contract_procedure(sender, **kwargs):
    return WorkshopContractProcedure().__class__


@receiver(register_modules)
def register_module(sender, **kwargs):
    return WorkshopsModule
