from django.dispatch import receiver

from resource_hub.core.signals import register_contract_procedures

from .models import VenueContractProcedure


@receiver(register_contract_procedures)
def register_contract_procedure(sender, **kwargs):
    return VenueContractProcedure().__class__
