# from django.shortcuts import render

# Create your views here.
"""Public-facing views for the core app."""

from django.views.generic import TemplateView


class LandingPageView(TemplateView):
    """Public marketing landing page.

    The full hero/features/FAQ/trust-feed build-out happens in a later
    phase once live platform metrics exist; for now this establishes the
    SaveCircle visual identity.
    """

    template_name = "landing.html"
