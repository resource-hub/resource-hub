from django.urls import path, include
from django.conf.urls import url
import django.contrib.auth.views as auth
from . import views, api_ajax

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth.LogoutView.as_view(
        template_name='core/logout.html'), name='logout'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    path('terms/', views.admin, name='terms'),
    path('support/', views.support, name='support'),

    path('admin/', views.admin, name='admin'),
    url(r'^admin/account/profile/(?P<scope>\w{0,50})/$',
        views.account_profile,
        name='account_profile'),
    url(r'^admin/account/settings/(?P<scope>\w{0,50})/$',
        views.account_settings,
        name='account_settings'),

    url(r'^admin/organizations/$',
        views.organizations,
        name='organizations'),
    url(r'^admin/organizations/register/$',
        views.organizations_register,
        name='organizations_register'),
    url(r'^admin/organizations/profile/(?P<id>\w{0,50})/$',
        views.organizations_profile,
        name='organizations_profile'),
    url(r'^admin/organizations/profile/edit/(?P<id>\w{0,50})/(?P<scope>\w{0,50})/$',
        views.organizations_profile_edit,
        name='organizations_profile_edit'),
    url(r'^admin/organizations/members/(?P<id>\w{0,50})/$',
        views.organizations_members,
        name='organizations_members'),
    url(r'^admin/organizations/members/add/(?P<id>\w{0,50})/$',
        views.organizations_members_add,
        name='organizations_members_add'),

    url(r'^api/user/search/$', api_ajax.UserSearch.as_view()),
    url(r'^api/organization/member/role/$',
        api_ajax.OrganizationMemberChangeRole.as_view()),
]
