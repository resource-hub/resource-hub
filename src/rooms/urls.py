from django.urls import path
from django.conf.urls import url

from core.urls import admin_urls, api_urls
from rooms import views, api

app_name = 'rooms'

api_urls.register([
    url(r'^rooms/$', api.Rooms.as_view(), name='rooms'),
    url(r'^rooms/(?P<room_id>\w{0,50})/events/$',
        api.RoomEvents.as_view(), name='rooms_event_feed'),
])

admin_urls.register([
    url(r'^rooms/manage/$', views.RoomsManage.as_view(), name='rooms_manage'),
    url(r'^rooms/manage/(?P<room_id>\w{0,50})/profile/edit/$',
        views.RoomsProfileEdit.as_view(), name='rooms_profile_edit'),
    url(r'^rooms/create/$', views.RoomsCreate.as_view(), name='rooms_create'),
])

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^(?P<room_id>\w{0,50})/details$',
        views.RoomDetails.as_view(), name='room_details'),
    url(r'^(?P<room_id>\w{0,50})/events/create/$',
        views.RoomEventsCreate.as_view(), name='events_create'),

]
