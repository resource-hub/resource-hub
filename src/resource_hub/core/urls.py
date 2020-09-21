import django.contrib.auth.views as dj_auth
from django.urls import include, path, re_path
from django.views.i18n import JavaScriptCatalog

from resource_hub.api.urls import api_urls
from resource_hub.control.urls import control_urls
from resource_hub.core.views import api, auth, control, site

from .hooks import UrlHook

finance_urls = UrlHook()
finance_urls.register([
    path('bank-accounts/', control.FinanceBankAccounts.as_view(),
         name='finance_bank_accounts'),
    path('payment-methods/manage/',
         control.FinancePaymentMethodsManage.as_view(), name='finance_payment_methods_manage'),
    path('payment-methods/manage/<int:pk>/', control.FinancePaymentMethodsEdit.as_view(
    ), name='finance_payment_methods_edit'),
    path('payment-methods/add/<str:scope>/',
         control.FinancePaymentMethodsAdd.as_view(), name='finance_payment_methods_add'),
    path('contracts/credited/', control.FinanceContractsCredited.as_view(),
         name='finance_contracts_credited'),
    path('contracts/debited/', control.FinanceContractsDebited.as_view(),
         name='finance_contracts_debited'),
    path('contracts/manage/<int:pk>/', control.FinanceContractsManageDetails.as_view(),
         name='finance_contracts_manage_details'),
    path('contract-procedures/manage/', control.FinanceContractProceduresManage.as_view(),
         name='finance_contract_procedures_manage'),
    path('contract-procedures/create/', control.FinanceContractProceduresCreate.as_view(),
         name='finance_contract_procedures_create'),
    path('invoices/outgoing/', control.FinanceInvoicesOutgoing.as_view(),
         name='finance_invoices_outgoing'),
    path('invoices/incoming/', control.FinanceInvoicesIncoming.as_view(),
         name='finance_invoices_incoming'),
])

control_urls.register([
    # account
    path('', control.Home.as_view(), name='home'),
    path('account/settings/<str:scope>/',
         control.AccountSettings.as_view(),
         name='account_settings'),
    path('account/security/<str:scope>/',
         control.AccountSecurity.as_view(),
         name='account_security'),
    path('account/verification/resend', auth.VerificationResend.as_view(),
         name='account_verification_resend'),

    # notifications
    path('notifications/', control.Notifications.as_view(), name='notifications'),

    # finance
    path('finance/', include(finance_urls.get())),

    # organizations
    path('organizations/manage/',
         control.OrganizationsManage.as_view(),
         name='organizations_manage'),
    path('organizations/create/',
         control.OrganizationsCreate.as_view(),
         name='organizations_create'),
    path('organizations/manage/<int:organization_id>/profile/edit/<str:scope>/',
         control.OrganizationsProfileEdit.as_view(),
         name='organizations_profile_edit'),
    path('organizations/manage/<int:organization_id>/members/',
         control.OrganizationsMembers.as_view(),
         name='organizations_members'),
    path('organizations/manage/<int:organization_id>/members/add/',
         control.OrganizationsMembersAdd.as_view(),
         name='organizations_members_add'),
    path('organizations/manage/<int:organization_id>/profile/',
         control.OrganizationsProfile.as_view(),
         name='organizations_profile'),

    # locations
    path('locations/manage/', control.LocationsManage.as_view(),
         name='locations_manage'),
    path('locations/create/', control.LocationsCreate.as_view(),
         name='locations_create'),
    path('locations/manage/<int:pk>/', control.LocationsEdit.as_view(),
         name='locations_edit'),
])

api_urls.register([
    path('users/search/', api.UserSearch.as_view(), name='search_users'),
    path('actors/list', api.ActorList.as_view(), name='actor_list'),
    path('actors/change',
         api.ActorChange.as_view(), name='actor_change'),
    path('organizations/<int:organization_pk>/members/change', api.OrganizationMembersChange.as_view(),
         name='organizations_members_change'),
    path('locations/search/', api.Locations.as_view(),
         name='locations_search'),
    path('contracts/list', api.ContractsList.as_view(), name='contracts_list'),
    path('notifications/list', api.NotificationsList.as_view(),
         name='notifications_list'),
    path('notifications/unread', api.NotificationsUnread.as_view(),
         name='notifications_unread'),
    path('notifications/mark/read/', api.NotificationsMarkRead.as_view(),
         name='notifications_mark_read'),
])

app_name = 'core'
urlpatterns = [
    # site
    path('', site.index, name='index'),
    path('home/', site.Home.as_view(), name='home'),
    path('bug/', site.ReportBug.as_view(), name='report_bug'),
    path('language/', site.Language.as_view(), name='language'),
    path('terms/', site.Terms.as_view(), name='terms'),
    path('imprint/', site.Imprint.as_view(), name='imprint'),
    path('privacy/', site.DataPrivacyStatement.as_view(), name='privacy'),
    path('locations/<slug:slug>/',
         site.LocationsProfile.as_view(), name='locations_profile'),
    path('actor/<slug:slug>/',
         site.ActorProfile.as_view(),
         name='actor_profile'),

    # path
    path('register/', auth.Register.as_view(), name='register'),
    path('login/', auth.custom_login, name='login'),
    path('logout/', dj_auth.LogoutView.as_view(
        template_name='core/logout.html'), name='logout'),
    re_path(r'^verify/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            auth.Verify.as_view(), name='verify'),
    path('password/reset/', dj_auth.PasswordResetView.as_view(
        template_name='core/password_reset.html', success_url='/password/reset/done/', email_template_name='core/mail_password_reset.html'), name='password_reset'),
    path('password/reset/done/', dj_auth.PasswordResetDoneView.as_view(
        template_name='core/password_reset_done.html', ), name='password_reset_done'),
    re_path(r'^password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$', dj_auth.PasswordResetConfirmView.as_view(
        template_name='core/password_reset_confirm.html', success_url='/password/reset/complete/'), name='password_reset_confirm'),
    path('password/reset/complete/', dj_auth.PasswordResetCompleteView.as_view(
        template_name='core/password_reset_complete.html')),
    path('actor/set', auth.SetRole.as_view(), name='actor_set'),


    # locale stuff
    path('i18n/', include('django.conf.urls.i18n')),
    path('jsi18n.js', JavaScriptCatalog.as_view(
        packages=['recurrence']), name='jsi18n'),
]
