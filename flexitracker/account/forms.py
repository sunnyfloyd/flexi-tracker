from django import forms
from django.core.exceptions import ValidationError
from .models import Profile
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class UserCreationAccountForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ("username", "email")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["email"].required = True

    def clean_email(self):
        cd = self.cleaned_data
        user = get_user_model()

        if user.objects.filter(email=cd["email"]):
            raise ValidationError("User with this email address already exists.")
        return cd["email"]


class UserEditForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ("first_name", "last_name", "email")


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("about_you",)
