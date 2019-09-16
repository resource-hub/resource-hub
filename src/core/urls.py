from django.urls import path, include
from django.conf.urls import url
import django.contrib.auth.views as auth
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth.LogoutView.as_view(
        template_name='core/logout.html'), name='logout'),
    path('activate-account/', views.activate_account, name='activate-account'),
    path('activate/', views.activate, name='activate'),
    path('account/', views.account, name='account'),
    path('account/settings', views.account_settings, name='account-settings'),
    path('account/change-email', views.change_email, name='change-email'),
    path('account/change-password', views.change_password, name='change-password'),
    path('account/information', views.account_information,
         name='account-information'),
    path('terms/', views.account, name='terms'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
]
