import os

from django.shortcuts import reverse
from django.utils.translation import gettext_lazy as _


def get_parent(path):
    return os.path.dirname(os.path.dirname(path))


class BaseModule():
    '''
    Abstract class for all necessary information about a module within resource hub
    has to be registered via the register_module signal
    '''
    @property
    def verbose_name(self) -> str:
        raise NotImplementedError()

    def get_sidebar_modules(self, request) -> list:
        '''
        Items to be displayed in the top navigaion bar
        :return return list of dicts with the structure defined by sidebar_module_renderer
        '''
        raise NotImplementedError()

    def get_navbar_items(self, request) -> list:
        '''
        Items to be displayed in the top navigation
        :return return list of dicts with "name", "url"
        '''
        raise NotImplementedError()

    def get_location_profile_item(self, context) -> str:
        '''
        :return HTML string to be included in the location profile
        '''
        return ""


class CoreModule(BaseModule):
    @property
    def verbose_name(self):
        return _('Core')

    def get_navbar_items(self, request):
        return [
            {
                'header': _('Home'),
                'url': reverse('core:home'),
            }
        ]

    def get_sidebar_modules(self, request):
        from .signals import control_sidebar_finance
        additional_finance_items = list(
            *map(lambda x: x[1], control_sidebar_finance.send(None)))
        if request.user.pk == request.actor.pk:
            user_settings = {
                'header': _('Security'),
                'url': reverse('control:account_security', kwargs={'scope': 'email'}),
            }
        else:
            user_settings = None
        first_child = reverse('control:account_settings',
                              kwargs={'scope': 'info'})
        root = get_parent(first_child)
        result = [
            {
                'header': _('Account'),
                'url': os.path.dirname(root),
                'sub_items': [
                    {
                        'header': _('Settings'),
                        'url': first_child,
                    },
                    {
                        'header': _('Notifications'),
                        'url': reverse('control:notifications_settings'),
                    },
                    user_settings
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
                                'url': reverse('control:finance_payment_methods_add', kwargs={'scope': 'bnk'}),
                            }
                        ]
                    },
                    {
                        'header': _('Invoices'),
                        'url': get_parent(reverse('control:finance_invoices_outgoing')),
                        'subsub_items': [
                            {
                                'header': _('Outgoing'),
                                'url': reverse('control:finance_invoices_outgoing'),
                            },
                            {
                                'header': _('Incoming'),
                                'url': reverse('control:finance_invoices_incoming'),
                            }
                        ]
                    },
                    *additional_finance_items,
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
            },
        ]
        # organizations tab only visible if user
        if request.user.pk == request.actor.pk:
            result.append(
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
            )
        return result
