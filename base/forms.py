from django.forms import ModelForm,widgets
from .models import Room,User
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.db import models

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name','username','email','password1','password2']

class RoomForm(ModelForm):
    privacy = forms.ChoiceField(
        choices=Room.PRIVACY_CHOICES,
        widget=forms.RadioSelect,
        label="Room Visibility"
    )


    class Meta:
        model = Room
        fields = ['topic', 'name', 'description', 'privacy','password']  # explicitly list fields




class UserForm(ModelForm):

    class Meta:
        fields=['avatar','name','username','email','bio']
        model = User
