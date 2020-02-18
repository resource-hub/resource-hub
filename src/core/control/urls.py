from django.conf.urls import url
from django.urls import include, path

from core.hooks import UrlHook

app_name = 'control'

control_urls = UrlHook()
urlpatterns = [
    path('', include(control_urls.get())),
]
