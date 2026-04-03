from django.core.cache import cache

from core.languages import DEFAULT_LANGUAGE_CODE, normalize_language_code
from core.models import CMSBlock


class CMSPageContent(dict):
    def __init__(self, page_code):
        super().__init__()
        self.page_code = page_code

    def __missing__(self, key):
        return key.replace("_", " ").strip().title()


class CMSContentMap(dict):
    def __missing__(self, key):
        value = CMSPageContent(key)
        self[key] = value
        return value


def cms_language_codes():
    return [
        field.name.removeprefix("text_")
        for field in CMSBlock._meta.get_fields()
        if getattr(field, "name", "").startswith("text_")
    ]


def cms_text_field_names():
    return [f"text_{code}" for code in cms_language_codes()]


def split_cms_key(key, default_page=CMSBlock.Page.SHARED):
    if "." in key:
        return key.split(".", 1)
    return default_page, key


def _cms_cache_key(language_code):
    return f"core.cms.blocks.{language_code}"


def _normalized_text(value):
    return (value or "").strip()


def _fallback_codes(language_code):
    requested = normalize_language_code(language_code)
    codes = [requested, DEFAULT_LANGUAGE_CODE, *cms_language_codes()]
    ordered = []
    for code in codes:
        if code not in ordered:
            ordered.append(code)
    return ordered


def _humanize_key(key):
    return key.split(".")[-1].replace("_", " ").strip().title()


def _resolve_block_text(block, language_code):
    for code in _fallback_codes(language_code):
        value = _normalized_text(getattr(block, f"text_{code}", ""))
        if value:
            return value
    return _humanize_key(block.key)


def get_cms_map(language_code):
    normalized_language = normalize_language_code(language_code)
    cache_key = _cms_cache_key(normalized_language)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    block_map = CMSContentMap()
    queryset = CMSBlock.objects.filter(is_active=True).only("page", "key", "is_active", *cms_text_field_names())
    for block in queryset:
        page_code, slot = split_cms_key(block.key, default_page=block.page)
        page_bucket = block_map.setdefault(page_code, CMSPageContent(page_code))
        page_bucket[slot] = _resolve_block_text(block, normalized_language)

    cache.set(cache_key, block_map, 300)
    return block_map


def get_cms_text(key, language_code, block_map=None):
    blocks = block_map if block_map is not None else get_cms_map(language_code)
    page_code, slot = split_cms_key(key)
    value = _normalized_text(blocks[page_code].get(slot, ""))
    if value:
        return value
    return _humanize_key(key)


def clear_cms_cache():
    for code in cms_language_codes():
        cache.delete(_cms_cache_key(code))
