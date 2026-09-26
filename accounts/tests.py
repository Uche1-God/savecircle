"""
Phase 1 test suite — authentication, user model and role-based access.

Run with:
    python manage.py test accounts
Or via pytest:
    pytest accounts/
"""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse


def get_user():
    """Return the active User model (avoids a module-level get_user_model call)."""
    return get_user_model()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_user(email="test@example.com", password="TestPass99!", role=None, **kwargs):
    """Create a user for tests, defaulting to the Saver role."""
    user_model = get_user()
    role = role or user_model.Role.SAVER
    return user_model.objects.create_user(
        email=email,
        password=password,
        full_name=kwargs.pop("full_name", "Test User"),
        role=role,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# User model
# ---------------------------------------------------------------------------


class UserModelTests(TestCase):
    def test_create_saver_sets_default_role(self):
        user_model = get_user()
        user = make_user()
        self.assertEqual(user.role, user_model.Role.SAVER)

    def test_email_is_username_field(self):
        user_model = get_user()
        self.assertEqual(user_model.USERNAME_FIELD, "email")

    def test_referral_code_auto_generated(self):
        user = make_user()
        self.assertTrue(user.referral_code)
        self.assertEqual(len(user.referral_code), 8)

    def test_referral_codes_are_unique(self):
        u1 = make_user(email="a@example.com")
        u2 = make_user(email="b@example.com")
        self.assertNotEqual(u1.referral_code, u2.referral_code)

    def test_is_saver_property(self):
        user = make_user()
        self.assertTrue(user.is_saver)
        self.assertFalse(user.is_platform_admin)
        self.assertFalse(user.is_super_admin)

    def test_is_admin_property(self):
        user_model = get_user()
        user = make_user(role=user_model.Role.ADMIN)
        self.assertTrue(user.is_platform_admin)
        self.assertFalse(user.is_saver)

    def test_is_super_admin_property(self):
        user_model = get_user()
        user = make_user(role=user_model.Role.SUPER_ADMIN)
        self.assertTrue(user.is_super_admin)

    def test_first_name_display_returns_first_token(self):
        user = make_user(full_name="Emeka Okonkwo")
        self.assertEqual(user.first_name_display, "Emeka")

    def test_first_name_display_falls_back_to_email(self):
        user = make_user(full_name="")
        self.assertIn("@", user.first_name_display)

    def test_str_returns_full_name(self):
        user = make_user(full_name="Amara Nwosu")
        self.assertEqual(str(user), "Amara Nwosu")

    def test_create_superuser_sets_super_admin_role(self):
        user_model = get_user()
        su = user_model.objects.create_superuser(
            email="super@savecircle.com",
            password="SuperPass1!",
        )
        self.assertEqual(su.role, user_model.Role.SUPER_ADMIN)
        self.assertTrue(su.is_staff)
        self.assertTrue(su.is_superuser)

    def test_referred_by_links_users(self):
        referrer = make_user(email="referrer@example.com")
        referred = make_user(email="referred@example.com", referred_by=referrer)
        self.assertEqual(referred.referred_by, referrer)
        self.assertIn(referred, referrer.referrals.all())


# ---------------------------------------------------------------------------
# Registration flow
# ---------------------------------------------------------------------------


class SignUpViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("accounts:signup")

    def test_signup_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_valid_signup_creates_user(self):
        user_model = get_user()
        response = self.client.post(
            self.url,
            {
                "full_name": "Chidi Okeke",
                "email": "chidi@example.com",
                "phone_number": "08012345678",
                "password1": "StrongPass99!",
                "password2": "StrongPass99!",
                "referral_code": "",
            },
        )
        self.assertEqual(user_model.objects.filter(email="chidi@example.com").count(), 1)
        user = user_model.objects.get(email="chidi@example.com")
        self.assertEqual(user.role, user_model.Role.SAVER)
        self.assertEqual(response.status_code, 302)

    def test_signup_with_referral_code_links_referrer(self):
        user_model = get_user()
        referrer = make_user(email="referrer@example.com")
        self.client.post(
            self.url,
            {
                "full_name": "New User",
                "email": "newuser@example.com",
                "phone_number": "07011111111",
                "password1": "StrongPass99!",
                "password2": "StrongPass99!",
                "referral_code": referrer.referral_code,
            },
        )
        new_user = user_model.objects.get(email="newuser@example.com")
        self.assertEqual(new_user.referred_by, referrer)

    def test_invalid_referral_code_raises_error(self):
        response = self.client.post(
            self.url,
            {
                "full_name": "Ghost User",
                "email": "ghost@example.com",
                "phone_number": "07022222222",
                "password1": "StrongPass99!",
                "password2": "StrongPass99!",
                "referral_code": "BADCODE1",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response.context["form"],
            "referral_code",
            "This referral code does not exist.",
        )

    def test_duplicate_email_rejected(self):
        user_model = get_user()
        make_user(email="taken@example.com")
        response = self.client.post(
            self.url,
            {
                "full_name": "Another Person",
                "email": "taken@example.com",
                "phone_number": "07033333333",
                "password1": "StrongPass99!",
                "password2": "StrongPass99!",
                "referral_code": "",
            },
        )
        self.assertEqual(user_model.objects.filter(email="taken@example.com").count(), 1)
        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_redirected_away_from_signup(self):
        user = make_user()
        self.client.force_login(user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)


# ---------------------------------------------------------------------------
# Login / logout
# ---------------------------------------------------------------------------


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("login")
        self.user = make_user(email="login@example.com", password="TestPass99!")

    def test_login_page_loads(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_valid_credentials_log_user_in(self):
        response = self.client.post(
            self.url,
            {"username": "login@example.com", "password": "TestPass99!"},
            follow=True,
        )
        self.assertTrue(response.context["user"].is_authenticated)

    def test_wrong_password_rejected(self):
        response = self.client.post(
            self.url,
            {"username": "login@example.com", "password": "WrongPassword!"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["user"].is_authenticated)


# ---------------------------------------------------------------------------
# Role-based dashboard access
# ---------------------------------------------------------------------------


class DashboardAccessTests(TestCase):
    def setUp(self):
        self.client = Client()
        user_model = get_user()
        self.saver = make_user(email="saver@example.com", role=user_model.Role.SAVER)
        self.admin = make_user(email="admin@example.com", role=user_model.Role.ADMIN)
        self.super_admin = make_user(email="super@example.com", role=user_model.Role.SUPER_ADMIN)

    # --- Saver dashboard ---
    def test_saver_can_access_saver_dashboard(self):
        self.client.force_login(self.saver)
        response = self.client.get(reverse("accounts:saver-dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_admin_blocked_from_saver_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("accounts:saver-dashboard"))
        self.assertEqual(response.status_code, 403)

    # --- Admin dashboard ---
    def test_admin_can_access_admin_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("accounts:admin-dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_super_admin_can_access_admin_dashboard(self):
        self.client.force_login(self.super_admin)
        response = self.client.get(reverse("accounts:admin-dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_saver_blocked_from_admin_dashboard(self):
        self.client.force_login(self.saver)
        response = self.client.get(reverse("accounts:admin-dashboard"))
        self.assertEqual(response.status_code, 403)

    # --- Super Admin dashboard ---
    def test_super_admin_can_access_super_admin_dashboard(self):
        self.client.force_login(self.super_admin)
        response = self.client.get(reverse("accounts:super-admin-dashboard"))
        self.assertEqual(response.status_code, 200)

    def test_admin_blocked_from_super_admin_dashboard(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("accounts:super-admin-dashboard"))
        self.assertEqual(response.status_code, 403)

    def test_saver_blocked_from_super_admin_dashboard(self):
        self.client.force_login(self.saver)
        response = self.client.get(reverse("accounts:super-admin-dashboard"))
        self.assertEqual(response.status_code, 403)

    # --- Dashboard redirect ---
    def test_dashboard_redirect_sends_saver_to_correct_url(self):
        self.client.force_login(self.saver)
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertRedirects(response, reverse("accounts:saver-dashboard"))

    def test_dashboard_redirect_sends_admin_to_correct_url(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertRedirects(response, reverse("accounts:admin-dashboard"))

    def test_dashboard_redirect_sends_super_admin_to_correct_url(self):
        self.client.force_login(self.super_admin)
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertRedirects(response, reverse("accounts:super-admin-dashboard"))

    def test_unauthenticated_user_redirected_to_login(self):
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/accounts/login/", response["Location"])


# ---------------------------------------------------------------------------
# Profile
# ---------------------------------------------------------------------------


class ProfileViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = make_user()

    def test_profile_page_requires_login(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)

    def test_profile_page_loads_for_authenticated_user(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 200)

    def test_profile_update_saves_full_name(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("accounts:profile"),
            {"full_name": "Updated Name", "phone_number": "08099999999"},
        )
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "Updated Name")


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------


class LandingPageTests(TestCase):
    def test_landing_page_returns_200(self):
        response = self.client.get(reverse("core:landing"))
        self.assertEqual(response.status_code, 200)

    def test_landing_page_contains_site_name(self):
        response = self.client.get(reverse("core:landing"))
        self.assertContains(response, "SaveCircle")
