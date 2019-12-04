from django import forms
from rooms.models import Room


class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        exclude = ['created_at']
