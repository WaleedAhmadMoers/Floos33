from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from core.languages import DEFAULT_LANGUAGE_CODE, SUPPORTED_LANGUAGE_CHOICES, SUPPORTED_LANGUAGE_CODES
from core.languages import normalize_language_code


LANGUAGE_COOKIE_NAME = "site_language"
LANGUAGE_PREFERENCE_SOURCE_COOKIE = "site_language_source"
LANGUAGE_PROMPT_DISMISSED_COOKIE = "site_language_prompt_dismissed"
LANGUAGE_SOURCE_EXPLICIT = "explicit"
LANGUAGE_SOURCE_BROWSER = "browser"
LANGUAGE_SOURCE_DEFAULT = "default"
LANGUAGE_SOURCE_QUERY = "query"

LANGUAGE_LABELS = {code: label for code, label in SUPPORTED_LANGUAGE_CHOICES}


def language_label(language_code):
    return LANGUAGE_LABELS.get(normalize_language_code(language_code), LANGUAGE_LABELS[DEFAULT_LANGUAGE_CODE])


def map_browser_locale(language_code):
    code = (language_code or "").strip().lower().replace("_", "-")
    if not code:
        return None
    if code in SUPPORTED_LANGUAGE_CODES:
        return code
    base_code = code.split("-", 1)[0]
    if base_code in SUPPORTED_LANGUAGE_CODES:
        return base_code
    return None


def detect_browser_language(request):
    accept_language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")
    candidates = []
    for chunk in accept_language.split(","):
        piece = chunk.strip()
        if not piece:
            continue
        locale = piece
        quality = 1.0
        if ";" in piece:
            locale, params = piece.split(";", 1)
            locale = locale.strip()
            params = params.strip()
            if params.startswith("q="):
                try:
                    quality = float(params[2:])
                except (TypeError, ValueError):
                    quality = 1.0
        mapped = map_browser_locale(locale)
        if mapped:
            candidates.append((quality, mapped))
    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1] if candidates else None


def get_explicit_language_preference(request):
    cookie_language = map_browser_locale(request.COOKIES.get(LANGUAGE_COOKIE_NAME))
    if cookie_language:
        return cookie_language

    session_language = map_browser_locale(request.session.get("site_language"))
    if session_language:
        return session_language

    user = getattr(request, "user", None)
    if user and user.is_authenticated:
        user_language = map_browser_locale(getattr(user, "preferred_language", None))
        if user_language and user_language != DEFAULT_LANGUAGE_CODE:
            return user_language
    return None


def remove_language_query_param(url):
    parsed = urlsplit(url)
    filtered_query = [(key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True) if key != "lang"]
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(filtered_query, doseq=True), parsed.fragment))


def get_language_resolution(request):
    cached = getattr(request, "_language_resolution", None)
    if cached is not None:
        return cached

    url_language = map_browser_locale(request.GET.get("lang"))
    explicit_language = get_explicit_language_preference(request)
    detected_language = detect_browser_language(request)

    if url_language:
        active_language = url_language
        source = LANGUAGE_SOURCE_QUERY
    elif explicit_language:
        active_language = explicit_language
        source = LANGUAGE_SOURCE_EXPLICIT
    elif detected_language:
        active_language = detected_language
        source = LANGUAGE_SOURCE_BROWSER
    else:
        active_language = DEFAULT_LANGUAGE_CODE
        source = LANGUAGE_SOURCE_DEFAULT

    dismissed_language = map_browser_locale(request.COOKIES.get(LANGUAGE_PROMPT_DISMISSED_COOKIE))
    show_prompt = bool(
        not url_language
        and not explicit_language
        and detected_language
        and detected_language != DEFAULT_LANGUAGE_CODE
        and dismissed_language != detected_language
    )

    resolution = {
        "active_language": normalize_language_code(active_language),
        "source": source,
        "explicit_language": explicit_language,
        "detected_language": detected_language,
        "show_prompt": show_prompt,
        "dismissed_language": dismissed_language,
    }
    request._language_resolution = resolution
    return resolution
