"""Context processors for the core app."""

from django.conf import settings


def platform_settings(request):
    """Expose small, frequently-used platform values to every template.

    Larger, database-backed platform settings (fees, bonus rates, revenue
    splits, etc.) are introduced in a later phase via a ``Settings`` model
    managed from the Super Admin panel.
    """

    return {
        "SITE_NAME": "SaveCircle",
        "CURRENCY_SYMBOL": "\u20a6",  # NGN naira sign
        "REFERRAL_RATE_PERCENT": settings.REFERRAL_RATE_PERCENT,
        "MATURITY_BONUS_PERCENT": settings.MATURITY_BONUS_PERCENT,
        "PLATFORM_FEE_PERCENT": settings.PLATFORM_FEE_PERCENT,
    }
