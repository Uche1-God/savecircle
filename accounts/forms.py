"""Forms for registration, login and profile management."""

import typing

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _

from .models import User


class EmailAuthenticationForm(AuthenticationForm):
    """Login form that speaks in terms of "email" rather than "username"."""

    username = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"autofocus": True, "class": "form-control"}),
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
    )

    error_messages: typing.ClassVar = {
        **AuthenticationForm.error_messages,
        "invalid_login": _(
            "Please enter a correct email and password. Note that both "
            "fields may be case-sensitive."
        ),
    }


class SignUpForm(UserCreationForm):
    """Registration form for new Savers.

    Accepts an optional referral code; if it matches an existing user's
    referral code, the new account is linked to that referrer.
    """

    full_name = forms.CharField(
        label=_("Full name"),
        max_length=150,
        widget=forms.TextInput(attrs={"class": "form-control", "autofocus": True}),
    )
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )
    phone_number = forms.CharField(
        label=_("Phone number"),
        max_length=15,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "08012345678"}),
    )
    referral_code = forms.CharField(
        label=_("Referral code (optional)"),
        max_length=8,
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. 7K3PQX2M"}),
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("full_name", "email", "phone_number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].help_text = _(
            "Use at least 8 characters. Avoid common passwords or "
            "anything based on your personal details."
        )

    def clean_referral_code(self):
        code = self.cleaned_data.get("referral_code", "").strip().upper()
        if code and not User.objects.filter(referral_code=code).exists():
            raise forms.ValidationError(_("This referral code does not exist."))
        return code

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = User.Role.SAVER

        referral_code = self.cleaned_data.get("referral_code")
        if referral_code:
            user.referred_by = User.objects.filter(referral_code=referral_code).first()

        if commit:
            user.save()
        return user


class ProfileForm(forms.ModelForm):
    """Lets a logged-in user update their own profile details."""

    class Meta:
        model = User
        fields = ("full_name", "phone_number", "avatar")
        widgets: typing.ClassVar = {
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
