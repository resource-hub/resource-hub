from django.urls import include
from django.conf.urls import url
import django.contrib.auth.views as auth
from . import views, api_ajax

app_name = 'core'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register/$', views.register, name='register'),
    url(r'^login/$', views.custom_login, name='login'),
    url(r'^logout/$', auth.LogoutView.as_view(
        template_name='core/logout.html'), name='logout'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^terms/$', views.admin, name='terms'),
    url(r'^support/$', views.support, name='support'),
    url(r'^language/$', views.language, name='language'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^set_role/$', views.set_role, name='set_role'),

    url(r'^admin/$', views.admin, name='admin'),
    url(r'^admin/account/profile/(?P<scope>\w{0,50})/$',
        views.account_profile,
        name='account_profile'),
    url(r'^admin/account/settings/(?P<scope>\w{0,50})/$',
        views.account_settings,
        name='account_settings'),

    url(r'^admin/organizations/manage$',
        views.organizations_manage,
        name='organizations_manage'),
    url(r'^admin/organizations/create/$',
        views.organizations_create,
        name='organizations_create'),
    url(r'^admin/organizations/manage/profile/(?P<organization_id>\w{0,50})/$',
        views.organizations_profile,
        name='organizations_profile'),
    url(r'^admin/organizations/manage/profile/edit/(?P<organization_id>\w{0,50})/(?P<scope>\w{0,50})/$',
        views.organizations_profile_edit,
        name='organizations_profile_edit'),
    url(r'^admin/organizations/manage/members/(?P<organization_id>\w{0,50})/$',
        views.organizations_members,
        name='organizations_members'),
    url(r'^admin/organizations/manage/members/add/(?P<organization_id>\w{0,50})/$',
        views.organizations_members_add,
        name='organizations_members_add'),

    url(r'^api/user/search/$', api_ajax.UserSearch.as_view()),
    url(r'^api/user/roles/$', api_ajax.UserRoles.as_view()),
    url(r'^api/organization/member/role/$',
        api_ajax.OrganizationMemberChangeRole.as_view()),
]
