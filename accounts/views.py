# from django.shortcuts import render
"""Views for registration, profile management and dashboard routing."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, RedirectView, TemplateView, UpdateView

from .forms import ProfileForm, SignUpForm
from .mixins import AdminRequiredMixin, SaverRequiredMixin, SuperAdminRequiredMixin
from .models import User


class SignUpView(CreateView):
    """Public registration for new Savers."""

    form_class = SignUpForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("accounts:dashboard")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_initial(self):
        initial = super().get_initial()
        ref = self.request.GET.get("ref")
        if ref:
            initial["referral_code"] = ref.upper()
        return initial

    def form_valid(self, form):
        response = super().form_valid(form)
        # With axes installed there are two authentication backends.
        # Django requires an explicit backend argument when multiple
        # backends are configured and the user object has no .backend set.
        login(
            self.request,
            self.object,
            backend="django.contrib.auth.backends.ModelBackend",
        )
        messages.success(
            self.request,
            f"Welcome to SaveCircle, {self.object.first_name_display}! "
            "Your account has been created.",
        )
        return response


class ProfileView(LoginRequiredMixin, UpdateView):
    """Lets a logged-in user view and edit their own profile."""

    model = User
    form_class = ProfileForm
    template_name = "accounts/profile.html"
    success_url = reverse_lazy("accounts:profile")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Your profile has been updated.")
        return super().form_valid(form)


class DashboardRedirectView(LoginRequiredMixin, RedirectView):
    """Sends a logged-in user to the dashboard for their role."""

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        role_urls = {
            User.Role.SAVER: "accounts:saver-dashboard",
            User.Role.ADMIN: "accounts:admin-dashboard",
            User.Role.SUPER_ADMIN: "accounts:super-admin-dashboard",
        }

        return reverse(role_urls.get(self.request.user.role, "accounts:saver-dashboard"))


class SaverDashboardView(SaverRequiredMixin, TemplateView):
    """Saver home dashboard (savings metrics land here in Phase 5)."""

    template_name = "dashboards/saver_dashboard.html"


class AdminDashboardView(AdminRequiredMixin, TemplateView):
    """Admin dashboard for managing assigned members (Phase 2+)."""

    template_name = "dashboards/admin_dashboard.html"


class SuperAdminDashboardView(SuperAdminRequiredMixin, TemplateView):
    """Platform-wide Super Admin dashboard (Phase 5+)."""

    template_name = "dashboards/super_admin_dashboard.html"
