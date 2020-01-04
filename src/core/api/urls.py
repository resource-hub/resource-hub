from django.urls import path, include
from django.conf.urls import url

from core.hooks import UrlHook


app_name = 'api'

api_urls = UrlHook()
urlpatterns = [
    path('', include(api_urls.get())),
]
