import uuid

from django.db import models
from django.forms import model_to_dict
from django.utils.translation import gettext_lazy as _
from resource_hub.core.models import BaseStateMachine


def get_types() -> list:
    return []


TYPES = get_types()


class BaseEvent(BaseStateMachine):
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

    uuid = models.UUIDField(
        default=uuid.uuid4,
    )
    context = models.JSONField()

    @property
    def verbose_name(self):
        return 'Base event'

    @property
    def type_(self):
        return self.TYPE

    def set_published(self):
        self.move_to(self.STATE.PUBLISHED)

    @classmethod
    def build_context(cls, kwargs) -> dict:
        raise NotImplementedError

    @classmethod
    def build(cls, **kwargs) -> dict:
        cls.objects.create(
            context=cls.build_context(kwargs),
        )

    class Meta:
        abstract = True


class ContractEvent(BaseEvent):
    contract = models.ForeignKey(
        'Contract',
        on_delete=models.CASCADE,
        related_name='events',
    )

    @classmethod
    def build(cls, contract, **kwargs) -> dict:
        cls.objects.create(
            contract=contract,
            context=cls.build_context(kwargs),
        )

    @classmethod
    def build_context(cls, kwargs):
        return {}


class StateChangedEvent(ContractEvent):
    TYPE = 'st_ev'

    @classmethod
    def build_context(cls, kwargs) -> dict:
        return {
            'new_state': kwargs['new_state'],
        }


class InvoiceCreatedEvent(ContractEvent):
    TYPE = 'ic_ev'

    @classmethod
    def build_context(cls, kwargs) -> dict:
        return {
            'invoice': model_to_dict(kwargs['invoice']),
            'positions': kwargs['invoice'].positions.values()
        }
