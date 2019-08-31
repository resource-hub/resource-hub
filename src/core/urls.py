from django.urls import path, include
import django.contrib.auth.views as auth
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.custom_login, name='login'),
    path('logout/', auth.LogoutView.as_view(
        template_name='core/account/logout.html'), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('terms/', views.profile, name='terms'),
]
