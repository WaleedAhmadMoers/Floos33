from django.db import models
from django.utils import timezone

from core.models import Notification, TickerNews


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
    lang = None
    if getattr(request, "user", None) and request.user.is_authenticated:
        lang = (request.user.preferred_language or "").lower()
    if not lang:
        lang = (getattr(request, "LANGUAGE_CODE", None) or "").lower()
    if not lang:
        lang = "en"

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

    return {"ticker_items": items, "ticker_language": lang or "en", "ticker_direction": direction}
