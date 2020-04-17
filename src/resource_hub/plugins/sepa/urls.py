from django.urls import path

from resource_hub.core.urls import finance_urls

from .views import (OpenPayments, SEPAMandateDetails, XMLFilesCreate,
                    XMLFilesManage)

app_name = 'sepa'
finance_urls.register([
    path('sepa/mandate/<int:mandate_pk>/<int:contract_pk>/',
         SEPAMandateDetails.as_view(), name='sepa_mandate'),
    path('sepa/manage/', XMLFilesManage.as_view(),
         name='finance_sepa_files_manage'),
    path('sepa/create/', XMLFilesCreate.as_view(),
         name='finance_sepa_files_create'),
    path('sepa/payments/open/', OpenPayments.as_view(),
         name='finance_sepa_open_payments'),
])

urlpatterns = [
]
