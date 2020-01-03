from django.urls import include, path
from django.conf.urls import url
import django.contrib.auth.views as auth
from django.views.i18n import JavaScriptCatalog

from . import views, api
from api.urls import api_urls

js_info_dict = {
    'packages': ('recurrence', ),
}

api_urls.register([
    url(r'^users/search/$', api.UserSearch.as_view(), name='search_users'),
    url(r'^actors/list$', api.ActorList.as_view(), name='actor_list'),
    url(r'^actors/change$',
        api.ActorChange.as_view(), name='actor_change'),
    url(r'locations/search/$', api.LocationFeed.as_view(),
        name='locations_search')
])

app_name = 'core'
urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^home/$', views.Home.as_view(), name='home'),

    url(r'^register/$', views.Register.as_view(), name='register'),
    url(r'^login/$', views.custom_login, name='login'),
    url(r'^logout/$', auth.LogoutView.as_view(
        template_name='core/logout.html'), name='logout'),
    url(r'^password/reset/$', auth.PasswordResetView.as_view(
        template_name='core/password_reset.html', success_url='/password/reset/done/', email_template_name='core/mail_password_reset.html'), name='password_reset'),
    url(r'^password/reset/done/$', auth.PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html', ), name='password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', auth.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html', success_url='/password/reset/complete/'), name='password_reset_confirm'),
    url(r'password/reset/complete/$', auth.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html')),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.Activate.as_view(), name='activate'),

    # todo termns an conditions
    url(r'^terms/$', views.Admin.as_view(), name='terms'),
    url(r'^support/$', views.Support.as_view(), name='support'),
    url(r'^language/$', views.Language.as_view(), name='language'),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), js_info_dict),
    url(r'^jsi18n.js$', JavaScriptCatalog.as_view(
        packages=['recurrence']), name='jsi18n'),
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

    url(r'^admin/locations/create/$', views.LocationCreate.as_view(),
        name='locations_create'),
    url(r'^admin/locations/manage/$', views.LocationManage.as_view(),
        name='locations_manage'),
]
