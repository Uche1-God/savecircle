"""Accounts models.

SaveCircle uses a single custom ``User`` model that doubles as the user's
profile (full name, phone number, avatar, referral code and role). This
keeps Phase 1 simple while still satisfying the "profiles" requirements
from the spec -- a separate ``Profile`` table can be split out later
without touching authentication if the need arises.
"""

import secrets
import string
import typing

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import UserManager

REFERRAL_CODE_LENGTH = 8
REFERRAL_CODE_ALPHABET = string.ascii_uppercase + string.digits

phone_number_validator = RegexValidator(
    regex=r"^\+?[0-9]{10,15}$",
    message=_("Enter a valid phone number, e.g. 08012345678 or +2348012345678."),
)


def generate_referral_code():
    """Return a random, URL-safe referral code (collision-checked on save)."""
    return "".join(secrets.choice(REFERRAL_CODE_ALPHABET) for _ in range(REFERRAL_CODE_LENGTH))


class User(AbstractUser):
    """SaveCircle platform user.

    Authentication uses ``email`` instead of ``username``. The inherited
    ``username`` field is kept (but unused/blank) because several
    Django internals -- including ``AbstractUser`` and the admin -- expect
    it to exist; it is hidden from all forms and templates.
    """

    class Role(models.TextChoices):
        SAVER = "saver", _("Saver")
        ADMIN = "admin", _("Admin")
        SUPER_ADMIN = "super_admin", _("Super Admin")

    username = None
    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(_("full name"), max_length=150)
    phone_number = models.CharField(
        _("phone number"),
        max_length=15,
        blank=True,
        validators=[phone_number_validator],
    )
    avatar = models.ImageField(_("avatar"), upload_to="avatars/%Y/%m/", blank=True, null=True)
    role = models.CharField(_("role"), max_length=20, choices=Role.choices, default=Role.SAVER)
    referral_code = models.CharField(
        _("referral code"), max_length=REFERRAL_CODE_LENGTH, unique=True, blank=True
    )
    referred_by = models.ForeignKey(
        "self",
        verbose_name=_("referred by"),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="referrals",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: typing.ClassVar = ["full_name"]

    objects = UserManager()

    class Meta:
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering: typing.ClassVar = ["-date_joined"]

    def __str__(self):
        return self.full_name or self.email

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self._generate_unique_referral_code()
        super().save(*args, **kwargs)

    def _generate_unique_referral_code(self):
        code = generate_referral_code()
        while User.objects.filter(referral_code=code).exists():
            code = generate_referral_code()
        return code

    @property
    def first_name_display(self):
        """First token of the full name, used for friendly greetings."""
        return self.full_name.split(" ")[0] if self.full_name else self.email

    @property
    def is_saver(self):
        return self.role == self.Role.SAVER

    @property
    def is_platform_admin(self):
        return self.role == self.Role.ADMIN

    @property
    def is_super_admin(self):
        return self.role == self.Role.SUPER_ADMIN
