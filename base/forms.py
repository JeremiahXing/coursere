from dataclasses import fields
from django.forms import ModelForm
from .models import Room, User, Profile

class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'topic', 'description']

class UserForm(ModelForm):
    class Meta:
        model=Profile
        fields=['avatar', 'bio']