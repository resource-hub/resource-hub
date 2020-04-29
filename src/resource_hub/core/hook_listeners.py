

from django.http import HttpRequest
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _

from .signals import register_modules


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


def navbar_item_renderer(structure: list, request) -> str:
    return render_to_string(
        'core/_navbar_items.html',
        context={
            'structure': structure,
        },
        request=request,
    )


def get_modules(map_function):
    result = []
    for module in map(map_function, register_modules.send(None)):
        result += module
    return result


def navigation_bar(context, *args, **kwargs):
    request = context.request
    modules = get_modules(lambda tuple: tuple[1]().get_navbar_items(request))
    return navbar_item_renderer(
        modules,
        request
    )


def control_sidebar(context, *args, **kwargs):
    request = context.request
    modules = get_modules(
        lambda tuple: tuple[1]().get_sidebar_modules(request))
    return sidebar_module_renderer(modules, request)
