"""Role-based access control mixins.

These mixins are layered on top of ``LoginRequiredMixin`` so that an
unauthenticated visitor is sent to the login page, while an
authenticated user with the wrong role gets a 403 Forbidden page rather
than being silently redirected -- which would leak the existence of
role-restricted pages.
"""

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from .models import User


class RoleRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Base mixin: only users whose ``role`` is in ``allowed_roles`` may pass."""

    allowed_roles: tuple[str, ...] = ()
    permission_denied_message = "You do not have permission to view this page."

    def test_func(self):
        return self.request.user.role in self.allowed_roles


class SaverRequiredMixin(RoleRequiredMixin):
    """Restrict a view to Saver accounts."""

    allowed_roles = (User.Role.SAVER,)


class AdminRequiredMixin(RoleRequiredMixin):
    """Restrict a view to Admins and Super Admins."""

    allowed_roles = (User.Role.ADMIN, User.Role.SUPER_ADMIN)


class SuperAdminRequiredMixin(RoleRequiredMixin):
    """Restrict a view to Super Admins only."""

    allowed_roles = (User.Role.SUPER_ADMIN,)
