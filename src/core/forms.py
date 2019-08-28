from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils.translation import gettext as _


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30, required=True, help_text=_('Pflichtfeld.'))
    last_name = forms.CharField(
        max_length=30, required=True, help_text=_('Pflichtfeld.'))
    email = forms.EmailField(
        max_length=254, help_text=_('Pflichtfeld.'))

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name',
                  'email', 'password1', 'password2', )
