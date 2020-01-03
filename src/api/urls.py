from django.urls import path, include
from django.conf.urls import url

from core.hooks import UrlHook

api_urls = UrlHook()

app_name = 'api'

urlpatterns = [
    path('', include(api_urls.get())),
]
