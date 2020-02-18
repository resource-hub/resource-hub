"""
resource_hub URL Configuration

"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    # apps
    path('', include('core.urls')),
    path('api/', include('core.api.urls')),
    path('control/', include('core.control.urls')),
    path('venues/', include('venues.urls')),

    # external apps
    path('dj-admin', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    path('summernote/', include('django_summernote.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
