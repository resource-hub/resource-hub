from django.apps import AppConfig

from core.hooks import hook
from venues.hook_listeners import admin_sidebar, navigation_bar, location_profile


class VenuesConfig(AppConfig):
    name = 'venues'

    hook.register('admin_sidebar', admin_sidebar)
    hook.register('navigation_bar', navigation_bar)
    hook.register('location_profile', location_profile)
