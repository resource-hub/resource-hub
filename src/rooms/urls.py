from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'rooms'
urlpatterns = [
    path('', views.index, name='index'),
    url(r'^rooms/manage/$', views.Manage.as_view(), name='manage'),
    url(r'^rooms/create/$', views.Create.as_view(), name='create'),
]
