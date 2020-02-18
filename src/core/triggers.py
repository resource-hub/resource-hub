from core.models import Contract


class BaseTrigger():
    @property
    def meta(self) -> dict:
        raise NotImplementedError()

    @property
    def fixed_condtion(self) -> bool:
        return False

    @property
    def default_condition(self) -> str:
        return Contract.STATE_PENDING


class BasePaymentMethod(BaseTrigger):
    @property
    def meta(self):
        raise NotImplementedError()

    @property
    def fixed_condtion(self) -> bool:
        return True

    def default_condition(self) -> str:
        return Contract.STATE_ACCEPTED

    def test(self):
        return 'test'
