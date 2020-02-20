from django.conf.urls import url

from core.control.urls import control_urls

from .views import BankTransferCreate

app_name = 'bank_transfer'


def register_urls():
    '''
    Wrapper for registering urls in other namespaces when app ist ready
    '''
    control_urls.register([
        url(r'^bank-transfer/create$', BankTransferCreate.as_view(),
            name='bank_transfer_create'),
    ])


urlpatterns = [

]
