"""
resource_hub URL Configuration

"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # apps
    path('', include('core.urls')),
    path('api/', include('core.api.urls')),
    path('admin/', include('core.admin.urls')),
    path('rooms/', include('rooms.urls')),

    # external apps
    path('django-rq/', include('django_rq.urls')),
    path('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
