from django.urls import path, include
import django.contrib.auth.views as auth
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth.LoginView.as_view(template_name='core/login.html',
                                          redirect_field_name=''), name="login"),
    path('logout/', auth.LoginView.as_view(template_name='core/login.html'), name="logout"),
]
