import logging
from datetime import datetime

from django.db import models
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _
from resource_hub.core.models import BaseStateMachine


def get_types() -> list:
    return []


TYPES = get_types()


class Event(BaseStateMachine):
    class STATE(BaseStateMachine.STATE):
        PUBLISHED = 'ps'

    STATES = [
        *BaseStateMachine.STATES,
        (STATE.PUBLISHED, _('published')),
    ]

    STATE_GRAPH = {
        STATE.PENDING: {STATE.PUBLISHED},
    }

    # unique char, that identifies the event type
    TYPE = 'ba_ev'

    context = models.JSONField()

    @classmethod
    def build(cls, **kwargs) -> dict:
        Event.objects.create(
            context=cls.build_context(*kwargs),
        )

    def build_context(self, **kwargs) -> dict:
        raise NotImplementedError

    @property
    def verbose_name(self):
        return 'Base event'

    @property
    def type_(self):
        return self.TYPE


class BaseContractEvent(Event):
    contract = models.ForeignKey(
        'Contract',
        on_delete=models.CASCADE,
        related_name='events',
    )

    class Meta:
        abstract = True


class StateChangedEvent(BaseContractEvent):
    TYPE = 'st_ev'

    def build_context(self, **kwargs) -> dict:
        return {
            'new_state': kwargs['new_state'],
        }


class InvoiceCreatedEvent(BaseContractEvent):
    TYPE = 'ic_ev'

    def build_context(self, **kwargs) -> dict:
        return {
            'invoice': model_to_dict(kwargs['invoice']),
            'positions': kwargs['invoice'].positions.values()
        }
