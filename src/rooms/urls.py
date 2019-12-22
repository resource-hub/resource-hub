from django.urls import path
from django.conf.urls import url

from rooms import views, api

app_name = 'rooms'
urlpatterns = [
    path('', views.index, name='index'),
    url(r'^manage/$', views.RoomsManage.as_view(), name='manage'),
    url(r'^create/$', views.RoomsCreate.as_view(), name='create'),
    url(r'^(?P<room_id>\w{0,50})/details$',
        views.RoomDetails.as_view(), name='room_details'),
    url(r'^(?P<room_id>\w{0,50})/events/create/$',
        views.RoomEventsCreate.as_view(), name='events_create'),

    url(r'api/rooms/$', api.Rooms.as_view(), name='api_room_feed'),
    url(r'api/(?P<room_id>\w{0,50})/events/$',
        api.RoomEvents.as_view(), name='api_room_event_feed'),
]
