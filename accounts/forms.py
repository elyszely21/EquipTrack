from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import UserProfile


class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())

    middle_name = forms.CharField(required=False)
    suffix = forms.CharField(required=False)
    contact_number = forms.CharField()

    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password"
        ]

    def clean(self):
        cleaned_data = super().clean()

        password = cleaned_data.get("password")
        confirm = cleaned_data.get("confirm_password")

        if password != confirm:
            raise forms.ValidationError(
                "Passwords do not match."
            )

        return cleaned_data


class LoginForm(AuthenticationForm):

    username = forms.CharField()

    password = forms.CharField(
        widget=forms.PasswordInput()
    )

    remember_me = forms.BooleanField(required=False)
