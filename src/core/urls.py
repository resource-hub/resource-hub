import django.contrib.auth.views as dj_auth
from django.conf.urls import url
from django.urls import include
from django.views.i18n import JavaScriptCatalog

from core.api.urls import api_urls
from core.panel.urls import admin_urls
from core.views import admin, api, auth, site

JS_INFO_DICT = {
    'packages': ('recurrence', ),
}

admin_urls.register([
    url(r'^$', admin.Home.as_view(), name='home'),
    url(r'^account/profile/(?P<scope>\w{0,50})/$',
        admin.AccountProfile.as_view(),
        name='account_profile'),
    url(r'^account/settings/(?P<scope>\w{0,50})/$',
        admin.AccountSettings.as_view(),
        name='account_settings'),

    url(r'^organizations/manage$',
        admin.OrganizationsManage.as_view(),
        name='organizations_manage'),
    url(r'^organizations/create/$',
        admin.OrganizationsCreate.as_view(),
        name='organizations_create'),
    url(r'^organizations/manage/(?P<organization_id>\w{0,50})/profile/$',
        admin.OrganizationsProfile.as_view(),
        name='organizations_profile'),
    url(r'^organizations/manage/(?P<organization_id>\w{0,50})/profile/edit/(?P<scope>\w{0,50})/$',
        admin.OrganizationsProfileEdit.as_view(),
        name='organizations_profile_edit'),
    url(r'^organizations/manage/(?P<organization_id>\w{0,50})/members/$',
        admin.OrganizationsMembers.as_view(),
        name='organizations_members'),
    url(r'^organizations/manage/(?P<organization_id>\w{0,50})/members/add/$',
        admin.OrganizationsMembersAdd.as_view(),
        name='organizations_members_add'),

    url(r'^locations/create/$', admin.LocationsCreate.as_view(),
        name='locations_create'),
    url(r'^locations/manage/$', admin.LocationsManage.as_view(),
        name='locations_manage'),
    url(r'^locations/manage/(?P<location_id>\w{0,50})/profile/edit$', admin.LocationsProfileEdit.as_view(),
        name='locations_profile_edit'),
])

api_urls.register([
    url(r'^users/search/$', api.UserSearch.as_view(), name='search_users'),
    url(r'^actors/list$', api.ActorList.as_view(), name='actor_list'),
    url(r'^actors/change$',
        api.ActorChange.as_view(), name='actor_change'),
    url(r'locations/search/$', api.Locations.as_view(),
        name='locations_search')
])

app_name = 'core'
urlpatterns = [
    url(r'^$', site.index, name='index'),
    url(r'^home/$', site.Home.as_view(), name='home'),
    url(r'^bug/$', site.ReportBug.as_view(), name='report_bug'),
    url(r'^language/$', site.Language.as_view(), name='language'),
    url(r'^terms/$', site.Terms.as_view(), name='terms'),

    url(r'^register/$', auth.Register.as_view(), name='register'),
    url(r'^login/$', auth.custom_login, name='login'),
    url(r'^logout/$', dj_auth.LogoutView.as_view(
        template_name='core/logout.html'), name='logout'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth.Activate.as_view(), name='activate'),
    url(r'^password/reset/$', dj_auth.PasswordResetView.as_view(
        template_name='core/password_reset.html', success_url='/password/reset/done/', email_template_name='core/mail_password_reset.html'), name='password_reset'),
    url(r'^password/reset/done/$', dj_auth.PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html', ), name='password_reset_done'),
    url(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', dj_auth.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html', success_url='/password/reset/complete/'), name='password_reset_confirm'),
    url(r'^password/reset/complete/$', dj_auth.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html')),
    url(r'^actor/set$', auth.SetRole.as_view(), name='actor_set'),

    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^jsi18n/$', JavaScriptCatalog.as_view(), JS_INFO_DICT),
    url(r'^jsi18n.js$', JavaScriptCatalog.as_view(
        packages=['recurrence']), name='jsi18n'),

    url(r'^locations/(?P<location_id>\w{0,50})/$',
        site.LocationsProfile.as_view(), name='locations_profile'),
]
