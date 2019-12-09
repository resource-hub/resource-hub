from django.apps import AppConfig

from core.hooks import hook
from rooms.hook_listeners import admin_sidebar, navigation_bar


class RoomsConfig(AppConfig):
    name = 'rooms'

    hook.register('admin_sidebar', admin_sidebar)
    hook.register('navigation_bar', navigation_bar)
