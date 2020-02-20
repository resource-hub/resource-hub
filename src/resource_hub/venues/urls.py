from django.conf.urls import url
from django.urls import path

from resource_hub.core.urls import api_urls, control_urls
from resource_hub.venues import api, views

app_name = 'venues'

api_urls.register([
    url(r'^venues/$', api.Venues.as_view(), name='venues'),
    url(r'^venues/(?P<room_id>\w{0,50})/events/$',
        api.VenueEvents.as_view(), name='venues_event_feed'),
])

control_urls.register([
    url(r'^venues/manage/$', views.VenuesManage.as_view(), name='venues_manage'),
    url(r'^venues/manage/(?P<room_id>\w{0,50})/profile/edit/$',
        views.VenuesProfileEdit.as_view(), name='venues_profile_edit'),
    url(r'^venues/create/$', views.VenuesCreate.as_view(), name='venues_create'),
])

urlpatterns = [
    path('', views.index, name='index'),
    url(r'^(?P<room_id>\w{0,50})/details$',
        views.VenueDetails.as_view(), name='room_details'),
    url(r'^(?P<room_id>\w{0,50})/events/create/$',
        views.VenueEventsCreate.as_view(), name='events_create'),

]
