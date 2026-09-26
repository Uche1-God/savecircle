"""URL routes for the accounts app."""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("signup/", views.SignUpView.as_view(), name="signup"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path("dashboard/", views.DashboardRedirectView.as_view(), name="dashboard"),
    path(
        "dashboard/saver/",
        views.SaverDashboardView.as_view(),
        name="saver-dashboard",
    ),
    path(
        "dashboard/admin/",
        views.AdminDashboardView.as_view(),
        name="admin-dashboard",
    ),
    path(
        "dashboard/super-admin/",
        views.SuperAdminDashboardView.as_view(),
        name="super-admin-dashboard",
    ),
]
