"""
resource_hub URL Configuration

"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # apps
    path('', include('resource_hub.core.urls')),
    path('api/', include('resource_hub.api.urls')),
    path('control/', include('resource_hub.control.urls')),
    path('venues/', include('resource_hub.venues.urls')),

    # external apps
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    path('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
