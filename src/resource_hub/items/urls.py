from django.urls import path

from resource_hub.core.urls import api_urls, control_urls

from . import api, views

app_name = 'items'

api_urls.register([
    path('items/', api.Items.as_view(), name='items'),
    path('items/<int:pk>/bookings/', api.Bookings.as_view(), name='item_bookings'),
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
    path('items/bookings/credited', views.ItemBookingsCredited.as_view(),
         name='item_bookings_credited'),
    path('items/bookings/debited', views.ItemBookingsDebited.as_view(),
         name='item_bookings_debited'),
])

urlpatterns = [
    path('', views.index, name='index'),
    path('<slug:owner_slug>/<slug:item_slug>/',
         views.ItemsDetails.as_view(), name='details'),
    path('<slug:owner_slug>/<slug:item_slug>/feed.ics',
         views.ICSFeed(), name='ics_feed'),
    path('<slug:owner_slug>/<slug:item_slug>/book',
         views.ItemBookingsCreate.as_view(), name='book'),
    path('bookings/<int:pk>/', views.ItemBookings.as_view(),
         name='bookings'),
]
