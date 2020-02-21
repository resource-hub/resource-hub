
from django.apps import AppConfig
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


class ControlConfig(AppConfig):
    name = 'resource_hub.control'


default_app_config = 'resource_hub.control.ControlConfig'


def sidebar_module_renderer(structure: list, request) -> str:
    '''
    max depth is 2 levels
    structure = [
        {
            'header': 'root',
            'url': 'root/',
            'sub_items': [
                {
                    'header': 'child',
                    'url': 'root/child/',
                },
                {
                    'header': 'child2',
                    'url': 'root/child2/',
                    'subsub_items': [
                        {
                            'header': 'child-child2',
                            'url': 'root/child2/stuff/,
                        },
                        ...
                    ]
                },
                ...
            ],
        },
        ...
    ]
    '''
    if not isinstance(structure, list):
        raise TypeError(_('The structure has to be of the type list'))

    if request is None:
        raise ValueError(_('The request object needs to be set'))

    if not isinstance(request, HttpRequest):
        raise TypeError(
            _('The passed request object is not an instance of HttpRequest'))

    return render_to_string(
        'control/_sidebar_module.html',
        context={
            'structure': structure
        },
        request=request)
