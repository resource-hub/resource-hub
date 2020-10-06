from django.urls import path
from resource_hub.core.urls import api_urls, control_urls
from resource_hub.workshops import api, views

app_name = 'workshops'

api_urls.register([
    path('workshops/', api.Workshops.as_view(), name='workshops'),
    path('workshops/<int:pk>/events/',
         api.WorkshopEvents.as_view(), name='workshops_event_feed'),
])

control_urls.register([
    path('workshops/manage/', views.WorkshopsManage.as_view(),
         name='workshops_manage'),
    path('workshops/manage/<int:pk>/',
         views.WorkshopsEdit.as_view(), name='workshops_edit'),
    path('workshops/create/', views.WorkshopsCreate.as_view(),
         name='workshops_create'),
    path('workshops/contract-procedures/create', views.ContractProceduresCreate.as_view(),
         name='workshops_contract_procedures_create'),
    path('workshops/contract-procedures/edit/<int:pk>/', views.ContractProceduresEdit.as_view(),
         name='workshops_contract_procedures_edit'),
])

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:location_slug>/<slug:workshop_slug>',
         views.WorkshopsDetails.as_view(), name='workshop_details'),
    path('<slug:location_slug>/<slug:workshop_slug>/events/create/',
         views.EventsCreate.as_view(), name='events_create'),

]
