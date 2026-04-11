from django.db import models
from django.db.models import Q
from django.utils.text import Truncator

from core.languages import DEFAULT_LANGUAGE_CODE, SUPPORTED_LANGUAGE_CHOICES
from core.languages import is_rtl_language, normalize_language_code, translated_field_name


class TranslatableContentMixin(models.Model):
    original_language = models.CharField(
        "original language",
        max_length=2,
        choices=SUPPORTED_LANGUAGE_CHOICES,
        default=DEFAULT_LANGUAGE_CODE,
    )
    title_en = models.CharField("title (English)", max_length=255, blank=True)
    description_en = models.TextField("description (English)", blank=True)
    title_de = models.CharField("title (German)", max_length=255, blank=True)
    description_de = models.TextField("description (German)", blank=True)
    title_ar = models.CharField("title (Arabic)", max_length=255, blank=True)
    description_ar = models.TextField("description (Arabic)", blank=True)
    title_tr = models.CharField("title (Turkish)", max_length=255, blank=True)
    description_tr = models.TextField("description (Turkish)", blank=True)
    title_fa = models.CharField("title (Farsi)", max_length=255, blank=True)
    description_fa = models.TextField("description (Farsi)", blank=True)
    title_fr = models.CharField("title (French)", max_length=255, blank=True)
    description_fr = models.TextField("description (French)", blank=True)
    title_es = models.CharField("title (Spanish)", max_length=255, blank=True)
    description_es = models.TextField("description (Spanish)", blank=True)
    title_pt = models.CharField("title (Portuguese)", max_length=255, blank=True)
    description_pt = models.TextField("description (Portuguese)", blank=True)
    title_nl = models.CharField("title (Dutch)", max_length=255, blank=True)
    description_nl = models.TextField("description (Dutch)", blank=True)
    title_zh = models.CharField("title (Chinese)", max_length=255, blank=True)
    description_zh = models.TextField("description (Chinese)", blank=True)

    class Meta:
        abstract = True

    @staticmethod
    def _normalized_text(value):
        return (value or "").strip()

    def _translated_value(self, base_name, language_code):
        field_name = translated_field_name(base_name, language_code)
        return self._normalized_text(getattr(self, field_name, ""))

    def has_language_content(self, language_code):
        language_code = normalize_language_code(language_code)
        if self.original_language == language_code:
            return bool(self._normalized_text(self.title) and self._normalized_text(self.description))
        return bool(
            self._translated_value("title", language_code)
            and self._translated_value("description", language_code)
        )

    def get_language_title(self, language_code):
        language_code = normalize_language_code(language_code)
        if self.original_language == language_code:
            return self._normalized_text(self.title)
        return self._translated_value("title", language_code)

    def get_language_description(self, language_code):
        language_code = normalize_language_code(language_code)
        if self.original_language == language_code:
            return self._normalized_text(self.description)
        return self._translated_value("description", language_code)

    def is_visible_in_language(self, language_code):
        return self.has_language_content(language_code)

    def get_language_direction(self, language_code):
        return "rtl" if is_rtl_language(language_code) else "ltr"

    def prepare_for_language(self, language_code):
        self.public_language = normalize_language_code(language_code)
        self.public_title = self.get_language_title(self.public_language)
        self.public_description = self.get_language_description(self.public_language)
        self.public_content_direction = self.get_language_direction(self.public_language)
        self.public_meta_description = self.get_meta_description(self.public_language)
        return self

    def get_meta_description(self, language_code, length=165):
        return Truncator(self.get_language_description(language_code)).chars(length)

    @classmethod
    def visible_in_language_q(cls, language_code):
        language_code = normalize_language_code(language_code)
        title_field = translated_field_name("title", language_code)
        description_field = translated_field_name("description", language_code)
        return Q(original_language=language_code) | (
            Q(**{f"{title_field}__gt": ""}) & Q(**{f"{description_field}__gt": ""})
        )

    @classmethod
    def public_search_q(cls, language_code, search_term):
        search_term = (search_term or "").strip()
        if not search_term:
            return Q()

        language_code = normalize_language_code(language_code)
        translated_title = translated_field_name("title", language_code)
        translated_description = translated_field_name("description", language_code)

        original_language_query = Q(original_language=language_code) & (
            Q(title__icontains=search_term) | Q(description__icontains=search_term)
        )
        translated_language_query = (
            Q(**{f"{translated_title}__gt": ""})
            & Q(**{f"{translated_description}__gt": ""})
            & (
                Q(**{f"{translated_title}__icontains": search_term})
                | Q(**{f"{translated_description}__icontains": search_term})
            )
        )
        return original_language_query | translated_language_query


def prepare_objects_for_language(objects, language_code):
    for obj in objects:
        if hasattr(obj, "prepare_for_language"):
            obj.prepare_for_language(language_code)
    return objects
