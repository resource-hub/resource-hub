from django.urls import include
from django.conf.urls import url
import django.contrib.auth.views as auth
from . import views, api_ajax

from django.contrib.auth.views import LoginView

app_name = 'core'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home/$', views.Home.as_view(), name='home'),
    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^login/$', views.custom_login, name='login'),
    url(r'^logout/$', auth.LogoutView.as_view(
        template_name='core/logout.html'), name='logout'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.Activate.as_view(), name='activate'),
    # todo termns an conditions
    url(r'^terms/$', views.Admin.as_view(), name='terms'),
    url(r'^support/$', views.Support.as_view(), name='support'),
    url(r'^language/$', views.Language.as_view(), name='language'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^set_role/$', views.SetRole.as_view(), name='set_role'),

    url(r'^admin/$', views.Admin.as_view(), name='admin'),
    url(r'^admin/account/profile/(?P<scope>\w{0,50})/$',
        views.AccountProfile.as_view(),
        name='account_profile'),
    url(r'^admin/account/settings/(?P<scope>\w{0,50})/$',
        views.AccountSettings.as_view(),
        name='account_settings'),

    url(r'^admin/organizations/manage$',
        views.OrganizationsManage.as_view(),
        name='organizations_manage'),
    url(r'^admin/organizations/create/$',
        views.OrganizationCreate.as_view(),
        name='organizations_create'),
    url(r'^admin/organizations/manage/profile/(?P<organization_id>\w{0,50})/$',
        views.OrganizationsProfile.as_view(),
        name='organizations_profile'),
    url(r'^admin/organizations/manage/profile/edit/(?P<organization_id>\w{0,50})/(?P<scope>\w{0,50})/$',
        views.OrganizationProfileEdit.as_view(),
        name='organizations_profile_edit'),
    url(r'^admin/organizations/manage/members/(?P<organization_id>\w{0,50})/$',
        views.OrganizationMembers.as_view(),
        name='organizations_members'),
    url(r'^admin/organizations/manage/members/add/(?P<organization_id>\w{0,50})/$',
        views.OrganizationMembersAdd.as_view(),
        name='organizations_members_add'),

    url(r'^api/user/search/$', api_ajax.UserSearch.as_view()),
    url(r'^api/user/roles/$', api_ajax.UserRoles.as_view()),
    url(r'^api/organization/member/role/$',
        api_ajax.OrganizationMemberChangeRole.as_view()),
]
