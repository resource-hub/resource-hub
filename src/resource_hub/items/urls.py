from django.urls import path
from resource_hub.core.urls import api_urls, control_urls

from . import views

app_name = 'items'

api_urls.register([
    #     path('items/', api.Items.as_view(), name='items'),
    #     path('items/<int:pk>/events/',
    #          api.ItemEvents.as_view(), name='items_event_feed'),
])

control_urls.register([
    path('items/manage/', views.ItemsManage.as_view(), name='items_manage'),
    path('items/manage/<int:pk>/',
         views.ItemsEdit.as_view(), name='items_edit'),
    path('items/create/', views.ItemsCreate.as_view(), name='items_create'),
    path('items/contract-procedures/create', views.ContractProceduresCreate.as_view(),
         name='items_contract_procedures_create'),
    path('items/contract-procedures/edit/<int:pk>/', views.ContractProceduresEdit.as_view(),
         name='items_contract_procedures_edit'),
])

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:actor_slug>/<slug:item_slug>',
         views.ItemsDetails.as_view(), name='item_details'),
]
