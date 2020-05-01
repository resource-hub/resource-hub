from django.urls import path

from resource_hub.core.urls import api_urls, control_urls
from resource_hub.venues import api, views

app_name = 'venues'

api_urls.register([
    path('venues/', api.Venues.as_view(), name='venues'),
    path('venues/<int:pk>/events/',
         api.VenueEvents.as_view(), name='venues_event_feed'),
])

control_urls.register([
    path('venues/manage/', views.VenuesManage.as_view(), name='venues_manage'),
    path('venues/manage/<int:pk>/',
         views.VenuesEdit.as_view(), name='venues_edit'),
    path('venues/create/', views.VenuesCreate.as_view(), name='venues_create'),
    path('venues/contract-procedures/create', views.ContractProceduresCreate.as_view(),
         name='venues_contract_procedures_create'),
    path('venues/contract-procedures/edit/<int:pk>/', views.ContractProceduresEdit.as_view(),
         name='venues_contract_procedures_edit'),
])

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:location_slug>/<slug:venue_slug>',
         views.VenuesDetails.as_view(), name='venue_details'),
    path('<slug:location_slug>/<slug:venue_slug>/events/create/',
         views.EventsCreate.as_view(), name='events_create'),

]
