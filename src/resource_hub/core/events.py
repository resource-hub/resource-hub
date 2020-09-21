from django.forms import model_to_dict


class BaseEvent:
    def __init__(self, **kwargs):
        self._context = self._build_context(kwargs)

    def _build_context(self, kwargs) -> dict:
        raise NotImplementedError

    @property
    def context(self):
        return self._context


class StateChangedEvent(BaseEvent):
    def _build_context(self, kwargs) -> dict:
        return {
            'state': kwargs['state'],
        }


class InvoiceCreatedEvent(BaseEvent):
    def _build_context(self, kwargs) -> dict:
        return {
            'invoice': model_to_dict(kwargs['invoice']),
            'positions': kwargs['invoice'].positions.values()
        }
