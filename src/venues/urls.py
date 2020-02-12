from django.urls import path
from django.conf.urls import url

from core.urls import admin_urls, api_urls
from venues import views, api

app_name = 'venues'

api_urls.register([
    url(r'^venues/$', api.Rooms.as_view(), name='venues'),
    url(r'^venues/(?P<room_id>\w{0,50})/events/$',
        api.RoomEvents.as_view(), name='venues_event_feed'),
])

admin_urls.register([
    url(r'^venues/manage/$', views.RoomsManage.as_view(), name='venues_manage'),
    url(r'^venues/manage/(?P<room_id>\w{0,50})/profile/edit/$',
        views.RoomsProfileEdit.as_view(), name='venues_profile_edit'),
    url(r'^venues/create/$', views.RoomsCreate.as_view(), name='venues_create'),
])

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^(?P<room_id>\w{0,50})/details$',
        views.RoomDetails.as_view(), name='room_details'),
    url(r'^(?P<room_id>\w{0,50})/events/create/$',
        views.RoomEventsCreate.as_view(), name='events_create'),

]
