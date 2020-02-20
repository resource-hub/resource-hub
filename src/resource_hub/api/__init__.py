
from django.apps import AppConfig


class ApiConfig(AppConfig):
    name = 'resource_hub.api'


default_app_config = 'resource_hub.api.ApiConfig'
