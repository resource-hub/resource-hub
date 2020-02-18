from django.utils.translation import ugettext_lazy as _

from core.triggers import BasePaymentMethod


class BankTransfer(BasePaymentMethod):
    @property
    def meta(self):
        return {
            'name': _('bank transfer'),
            'provider': _('Resource Hub Team'),
            'logo': _('banktransfer/logo.png'),
        }
