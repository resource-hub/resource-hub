from django.conf.urls import url
from django.urls import path

from resource_hub.core.urls import api_urls, control_urls
from resource_hub.venues import api, views

app_name = 'venues'

api_urls.register([
    path('venues/', api.Venues.as_view(), name='venues'),
    path('venues/<int:venue_id>/events/',
         api.VenueEvents.as_view(), name='venues_event_feed'),
])

control_urls.register([
    path('venues/manage/', views.VenuesManage.as_view(), name='venues_manage'),
    path('venues/manage/<int:venue_id>/profile/edit/',
         views.VenuesProfileEdit.as_view(), name='venues_profile_edit'),
    path('venues/create/', views.VenuesCreate.as_view(), name='venues_create'),
])

urlpatterns = [
    path('', views.index, name='index'),
    path('<int:venue_id>/details',
         views.VenueDetails.as_view(), name='venue_details'),
    path('<int:venue_id>/events/create/',
         views.VenueEventsCreate.as_view(), name='events_create'),

]
