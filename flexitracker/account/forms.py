from django import forms
from .models import Profile
from django.contrib.auth import get_user_model

class UserEditForm(forms.ModelForm):
    
    class Meta:
        model = get_user_model()
        fields = ('first_name', 'last_name', 'email')

class ProfileEditForm(forms.ModelForm):
    
    class Meta:
        model = Profile
        fields = ('test_field',)

