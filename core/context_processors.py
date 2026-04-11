from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from core.cms import get_cms_map, get_cms_text
from core.language_runtime import get_language_resolution, language_label, remove_language_query_param
from core.languages import DEFAULT_LANGUAGE_CODE, is_rtl_language, normalize_language_code, site_language_options
from core.models import Notification, TickerNews


def resolve_site_language(request):
    return get_language_resolution(request)["active_language"]


def notifications(request):
    if request.user.is_authenticated:
        qs = Notification.objects.filter(recipient=request.user).order_by("-created_at")
        unread = qs.filter(is_read=False).count()
        recent = list(qs[:3])
    else:
        unread = 0
        recent = []
    return {"notifications_unread_count": unread, "notifications_recent": recent}


def cms_content(request):
    language_code = resolve_site_language(request)
    request._cms_blocks = get_cms_map(language_code)
    return {"cms": request._cms_blocks}


def ticker_news(request):
    """
    Expose ticker items from the dedicated ticker news model.
    """
    lang = resolve_site_language(request)
    now = timezone.now()
    user = getattr(request, "user", None)
    queryset = (
        TickerNews.objects.filter(is_active=True)
        .filter(models.Q(start_at__lte=now) | models.Q(start_at__isnull=True))
        .filter(models.Q(end_at__gte=now) | models.Q(end_at__isnull=True))
        .prefetch_related("translations")
        .order_by("-priority", "-created_at")
    )

    def pick_translation(item):
        translations = list(item.translations.all())
        if not translations:
            return None
        requested = normalize_language_code(lang)
        english = DEFAULT_LANGUAGE_CODE
        for code in (requested, english):
            for translation in translations:
                if (translation.language_code or "").lower().strip() == code:
                    return translation
        for translation in translations:
            if (translation.message or "").strip():
                return translation
        return None

    items = []
    for item in queryset:
        if item.audience == TickerNews.Audience.BUYERS and not (user and user.is_authenticated and user.is_buyer):
            continue
        if item.audience == TickerNews.Audience.SELLERS and not (user and user.is_authenticated and user.is_seller):
            continue
        if item.audience == TickerNews.Audience.VERIFIED and not (user and user.is_authenticated and user.is_verified_user):
            continue

        translation = pick_translation(item)
        if not translation:
            continue
        items.append(
            {
                "message": translation.message,
                "news_type": item.news_type,
                "link_url": item.link_url or "",
            }
        )

    direction = "rtl" if is_rtl_language(lang) else "ltr"

    return {
        "ticker_items": items,
        "ticker_language": lang or "en",
        "ticker_direction": direction,
        "current_site_language": lang or "en",
        "current_site_direction": direction,
        "site_language_choices": site_language_options(),
    }


def site_identity(request):
    resolver = getattr(request, "resolver_match", None)
    namespace = getattr(resolver, "namespace", "") or ""
    url_name = getattr(resolver, "url_name", "") or ""
    language_resolution = get_language_resolution(request)
    current_language = language_resolution["active_language"]
    cms_blocks = getattr(request, "_cms_blocks", None) or get_cms_map(current_language)

    seo_indexable = True
    if namespace in {"accounts", "companies", "inquiries", "admin"}:
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
    elif namespace == "blog" and url_name not in {"list", "detail"}:
        seo_indexable = False
    elif namespace == "core" and (
        url_name in {"saved", "notifications", "notification_read", "notification_read_all", "deal_status", "deal_identity_request", "support", "set_language"}
        or url_name.startswith("control")
    ):
        seo_indexable = False
    if any(key != "lang" for key in request.GET.keys()):
        seo_indexable = False
    requested_lang = normalize_language_code(request.GET.get("lang"))
    if request.GET.get("lang") and requested_lang == DEFAULT_LANGUAGE_CODE:
        seo_indexable = False

    site_origin = f"{request.scheme}://{request.get_host()}"
    canonical_path = request.path
    if namespace == "core" and url_name == "support":
        canonical_path = reverse("core:contact")
    canonical_url = f"{site_origin}{canonical_path}"
    if current_language != DEFAULT_LANGUAGE_CODE:
        canonical_url = f"{canonical_url}?lang={current_language}"
    support_whatsapp_url = f"https://wa.me/{''.join(ch for ch in settings.SUPPORT_PHONE if ch.isdigit())}"
    browser_detected_language = language_resolution["detected_language"]
    language_switch_next_url = remove_language_query_param(request.get_full_path())
    language_suggestion = {
        "show": language_resolution["show_prompt"],
        "language_code": browser_detected_language,
        "language_label": language_label(browser_detected_language) if browser_detected_language else "",
        "use_english_label": language_label(DEFAULT_LANGUAGE_CODE),
    }

    return {
        "site_name": settings.SITE_NAME,
        "support_email": settings.SUPPORT_EMAIL,
        "support_phone": settings.SUPPORT_PHONE,
        "support_whatsapp_url": support_whatsapp_url,
        "site_origin": site_origin,
        "canonical_url": canonical_url,
        "seo_indexable": seo_indexable,
        "current_site_language": current_language,
        "current_site_language_label": language_label(current_language),
        "current_site_direction": "rtl" if is_rtl_language(current_language) else "ltr",
        "site_language_choices": site_language_options(),
        "language_switch_next_url": language_switch_next_url,
        "language_suggestion": language_suggestion,
        "default_meta_description": get_cms_text("shared.default_meta_description", current_language, cms_blocks),
    }
