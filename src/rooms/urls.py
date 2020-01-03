from django.urls import path
from django.conf.urls import url

from core.urls import api_urls
from rooms import views, api

app_name = 'rooms'

api_urls.register([
    url(r'rooms/$', api.Rooms.as_view(), name='room_feed'),
    url(r'rooms/(?P<room_id>\w{0,50})/events/$',
        api.RoomEvents.as_view(), name='room_event_feed'),
])

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^manage/$', views.RoomsManage.as_view(), name='manage'),
    url(r'^create/$', views.RoomsCreate.as_view(), name='create'),
    url(r'^(?P<room_id>\w{0,50})/details$',
        views.RoomDetails.as_view(), name='room_details'),
    url(r'^(?P<room_id>\w{0,50})/events/create/$',
        views.RoomEventsCreate.as_view(), name='events_create'),

]
