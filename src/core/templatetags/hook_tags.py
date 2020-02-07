"""
Big thanks to https://github.com/nitely/django-hooks for providing the logic
"""
from django import template
from django.utils.html import format_html_join

from core.hooks import hook

register = template.Library()


@register.simple_tag(name="hook", takes_context=True)
def hook_tag(context, name, *args, **kwargs):
    """
    Hook tag to call within templates
    :param dict context: This is automatically passed,\
    contains the template state/variables
    :param str name: The hook which will be dispatched
    :param \*args: Positional arguments, will be passed to hook callbacks
    :param \*\*kwargs: Keyword arguments, will be passed to hook callbacks
    :return: A concatenation of all callbacks\
    responses marked as safe (conditionally)
    :rtype: str
    """
    # print(context)
    return format_html_join(
        sep="\n",
        format_string="{}",
        args_generator=(
            (response, )
            for response in hook(name, context, *args, **kwargs)
        )
    )
