from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _

from resource_hub.core.modules import get_parent
from resource_hub.core.signals import (control_sidebar_finance,
                                       register_payment_methods)

from .models import SEPA


@receiver(register_payment_methods)
def register_payment_method(sender, **kwargs):
    return SEPA()


@receiver(control_sidebar_finance)
def control_sidebar_finance_items(sender, **kwargs):
    return [
        {
            'header': _('SEPA'),
            'url': get_parent(reverse('control:finance_sepa_files_manage')),
            'subsub_items': [
                {
                    'header': _('Files manage'),
                    'url': reverse('control:finance_sepa_files_manage'),
                },
                {
                    'header': _('Files create'),
                    'url': reverse('control:finance_sepa_files_create'),
                },
                {
                    'header': _('Open payments'),
                    'url': reverse('control:finance_sepa_open_payments'),
                }
            ]
        },
    ]
