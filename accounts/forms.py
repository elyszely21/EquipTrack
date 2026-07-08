from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from .models import UserProfile, Staff


class UserRegistrationForm(forms.ModelForm):

    PUBLIC_ROLE_CHOICES = [
        (UserProfile.ROLE_BORROWER, "Borrower"),
        (UserProfile.ROLE_STAFF, "Staff"),
    ]

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"})
    )

    middle_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    suffix = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    contact_number = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    department = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    position = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"})
    )

    role = forms.ChoiceField(
        choices=PUBLIC_ROLE_CHOICES,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = User

        fields = [
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
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

    def clean_username(self):

        username = self.cleaned_data["username"]

        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError(
                "This username is already taken."
            )

        return username

    def clean_email(self):

        email = self.cleaned_data["email"]

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "This email address is already registered."
            )

        return email

    def clean_role(self):

        role = self.cleaned_data["role"]

        allowed_roles = {
            choice[0]
            for choice in self.PUBLIC_ROLE_CHOICES
        }

        if role not in allowed_roles:
            raise forms.ValidationError(
                "Invalid registration role."
            )

        return role

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        for field_name in [
            "username",
            "first_name",
            "last_name",
            "email",
        ]:

            self.fields[field_name].widget.attrs.update(
                {"class": "form-control"}
            )


class LoginForm(AuthenticationForm):

    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control"}
        )
    )

    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        )
    )

    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(
            attrs={"class": "form-check-input"}
        )
    )

# STAFF MANAGEMENT FORM

class StaffForm(forms.ModelForm):

    class Meta:

        model = Staff

        fields = [
            "department",
        ]

        widgets = {

            "department": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Department"
                }
            ),

        }