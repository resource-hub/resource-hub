from django.urls import path, include
from django.conf.urls import url

from core.hooks import UrlHook


app_name = 'panel'

admin_urls = UrlHook()
urlpatterns = [
    path('', include(admin_urls.get())),
]
