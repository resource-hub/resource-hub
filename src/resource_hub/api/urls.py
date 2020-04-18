from django.conf.urls import url
from django.urls import include, path

from resource_hub.core.hooks import UrlHook

app_name = 'api'
api_urls = UrlHook()
urlpatterns = [
    path('', include(api_urls.get())),
]
