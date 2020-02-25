"""
WSGI config for resource_hub project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/howto/deployment/wsgi/
"""


from django.core.wsgi import get_wsgi_application

from resource_hub.core.jobs import init_schedule

init_schedule()

application = get_wsgi_application()
