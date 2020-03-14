
import os

from django.shortcuts import reverse
from django.utils.translation import ugettext_lazy as _

from resource_hub.control import sidebar_module_renderer


def get_parent(path):
    return os.path.dirname(os.path.dirname(path))


def control_sidebar(context, *args, **kwargs):
    first_child = reverse('control:account_profile', kwargs={'scope': 'info'})
    root = get_parent(first_child)
    return sidebar_module_renderer(
        [
            {
                'header': _('Account'),
                'url': os.path.dirname(root),
                'sub_items': [
                    {
                        'header': _('Profile'),
                        'url': first_child,
                    },
                    {
                        'header': _('Settings'),
                        'url': reverse('control:account_settings', kwargs={'scope': 'email'}),
                    },
                ]
            },
            {
                'header': _('Finanace'),
                'url': get_parent(reverse('control:finance_bank_accounts')),
                'sub_items': [
                    {
                        'header': _('Contracts'),
                        'url': get_parent(reverse('control:finance_contracts_credited')),
                        'subsub_items': [
                            {
                                'header': _('Credited'),
                                'url': reverse('control:finance_contracts_credited'),
                            },
                            {
                                'header': _('Debited'),
                                'url': reverse('control:finance_contracts_debited'),
                            }
                        ]
                    },
                    {
                        'header': _('Contract procedures'),
                        'url': get_parent(reverse('control:finance_contract_procedures_manage')),
                        'subsub_items': [
                            {
                                'header': _('Manage'),
                                'url': reverse('control:finance_contract_procedures_manage'),
                            },
                            {
                                'header': _('Create'),
                                'url': reverse('control:finance_contract_procedures_create'),
                            }
                        ]
                    },
                    {
                        'header': _('Payment methods'),
                        'url': get_parent(reverse('control:finance_payment_methods_manage')),
                        'subsub_items': [
                            {
                                'header': _('Manage'),
                                'url': reverse('control:finance_payment_methods_manage'),
                            },
                            {
                                'header': _('Add'),
                                'url': reverse('control:finance_payment_methods_add'),
                            }
                        ]
                    },
                ]
            },
            {
                'header': _('Organizations'),
                'url': get_parent(reverse('control:organizations_manage')),
                'sub_items': [
                    {
                        'header': _('Manage'),
                        'url': reverse('control:organizations_manage'),
                    },
                    {
                        'header': _('Create'),
                        'url': reverse('control:organizations_create'),
                    }
                ]
            },
            {
                'header': _('Locations'),
                'url': get_parent(reverse('control:locations_manage')),
                'sub_items': [
                    {
                        'header': _('Manage'),
                        'url': reverse('control:locations_manage'),
                    },
                    {
                        'header': _('Create'),
                        'url': reverse('control:locations_create'),
                    },
                ]
            }
        ],
        request=context.request,
    )
