from django.urls import path
from django.conf.urls import url

from . import views

app_name = 'rooms'
urlpatterns = [
    path('', views.index, name='index'),
    url(r'^manage/$', views.RoomsManage.as_view(), name='manage'),
    url(r'^create/$', views.RoomsCreate.as_view(), name='create'),
    url(r'^events/create/$', views.EventsCreate.as_view(), name='events_create'),
]
