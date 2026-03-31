from django.db import models
from django.conf import settings
from django.utils import timezone

from core.models import Notification, TickerNews


SUPPORTED_SITE_LANGUAGES = {"en", "de", "ar"}


def resolve_site_language(request):
    lang = (request.session.get("site_language") or "").lower()
    if lang not in SUPPORTED_SITE_LANGUAGES and getattr(request, "user", None) and request.user.is_authenticated:
        lang = (request.user.preferred_language or "").lower()
    if lang not in SUPPORTED_SITE_LANGUAGES:
        lang = (getattr(request, "LANGUAGE_CODE", None) or "").lower()
    if lang not in SUPPORTED_SITE_LANGUAGES:
        lang = "en"
    return lang


def notifications(request):
    if request.user.is_authenticated:
        qs = Notification.objects.filter(recipient=request.user).order_by("-created_at")
        unread = qs.filter(is_read=False).count()
        recent = list(qs[:3])
    else:
        unread = 0
        recent = []
    return {"notifications_unread_count": unread, "notifications_recent": recent}


def ticker_news(request):
    """
    Expose ticker items based on user language and audience.
    """
    # Determine language preference
    lang = resolve_site_language(request)

    now = timezone.now()

    qs = (
        TickerNews.objects.filter(is_active=True)
        .filter(models.Q(start_at__lte=now) | models.Q(start_at__isnull=True))
        .filter(models.Q(end_at__gte=now) | models.Q(end_at__isnull=True))
        .prefetch_related("translations")
        .order_by("-priority", "-created_at")
    )

    user = getattr(request, "user", None)
    items = []

    for item in qs:
        # audience filtering
        if item.audience == TickerNews.Audience.BUYERS and not (user and user.is_authenticated and user.is_buyer):
            continue
        if item.audience == TickerNews.Audience.SELLERS and not (user and user.is_authenticated and user.is_seller):
            continue
        if item.audience == TickerNews.Audience.VERIFIED and not (user and user.is_authenticated and user.is_verified_user):
            continue

        # choose translation
        translation = None
        fallback = None
        for t in item.translations.all():
            code = (t.language_code or "").lower()
            if code == lang:
                translation = t
                break
            if code == "en":
                fallback = t
        translation = translation or fallback
        if not translation:
            continue

        items.append(
            {
                "message": translation.message,
                "news_type": item.news_type,
                "link_url": item.link_url,
            }
        )

    direction = "rtl" if lang.startswith("ar") else "ltr"

    return {
        "ticker_items": items,
        "ticker_language": lang or "en",
        "ticker_direction": direction,
        "current_site_language": lang or "en",
        "current_site_direction": direction,
    }


def site_identity(request):
    resolver = getattr(request, "resolver_match", None)
    namespace = getattr(resolver, "namespace", "") or ""
    url_name = getattr(resolver, "url_name", "") or ""

    seo_indexable = True
    if namespace in {"accounts", "companies", "inquiries"}:
        seo_indexable = False
    elif namespace == "stocklots" and url_name in {
        "mine",
        "favorites",
        "create",
        "edit",
        "mark_sold",
        "deactivate",
        "activate",
        "restore",
        "delete",
        "favorite_toggle",
    }:
        seo_indexable = False
    elif namespace == "rfqs" and url_name not in {"list", "detail"}:
        seo_indexable = False
    elif namespace == "core" and (
        url_name in {"saved", "notifications", "notification_read", "notification_read_all", "deal_status", "deal_identity_request", "support", "set_language"}
        or url_name.startswith("control")
    ):
        seo_indexable = False

    site_origin = f"{request.scheme}://{request.get_host()}"
    canonical_url = f"{site_origin}{request.path}"

    return {
        "site_name": settings.SITE_NAME,
        "support_email": settings.SUPPORT_EMAIL,
        "support_phone": settings.SUPPORT_PHONE,
        "site_origin": site_origin,
        "canonical_url": canonical_url,
        "seo_indexable": seo_indexable,
        "current_site_language": resolve_site_language(request),
        "default_meta_description": "floos33 is a B2B marketplace for EU stocklots, liquidation inventory, and buyer RFQs connecting EU sellers with MENA buyers.",
    }
