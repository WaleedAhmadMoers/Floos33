from django.conf import settings
from django.db import models
from django.db.models import Q
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.text import Truncator

from core.languages import DEFAULT_LANGUAGE_CODE, SUPPORTED_LANGUAGE_CHOICES
from core.languages import is_rtl_language, normalize_language_code, translated_field_name


def article_featured_image_upload_path(instance, filename):
    return f"blog/{instance.slug or 'article'}/{filename}"


class Article(models.Model):
    class Kind(models.TextChoices):
        NEWS = "news", "News"
        GUIDE = "guide", "Guide"
        TUTORIAL = "tutorial", "Tutorial"
        UPDATE = "update", "Platform update"
        INSIGHT = "insight", "Market insight"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    original_language = models.CharField(
        "original language",
        max_length=2,
        choices=SUPPORTED_LANGUAGE_CHOICES,
        default=DEFAULT_LANGUAGE_CODE,
    )
    kind = models.CharField("content type", max_length=20, choices=Kind.choices, default=Kind.NEWS)
    title = models.CharField("title", max_length=255)
    slug = models.SlugField("slug", max_length=280, unique=True, blank=True)
    body = models.TextField("body")
    title_en = models.CharField("title (English)", max_length=255, blank=True)
    body_en = models.TextField("body (English)", blank=True)
    title_de = models.CharField("title (German)", max_length=255, blank=True)
    body_de = models.TextField("body (German)", blank=True)
    title_ar = models.CharField("title (Arabic)", max_length=255, blank=True)
    body_ar = models.TextField("body (Arabic)", blank=True)
    title_tr = models.CharField("title (Turkish)", max_length=255, blank=True)
    body_tr = models.TextField("body (Turkish)", blank=True)
    title_fa = models.CharField("title (Farsi)", max_length=255, blank=True)
    body_fa = models.TextField("body (Farsi)", blank=True)
    title_fr = models.CharField("title (French)", max_length=255, blank=True)
    body_fr = models.TextField("body (French)", blank=True)
    title_es = models.CharField("title (Spanish)", max_length=255, blank=True)
    body_es = models.TextField("body (Spanish)", blank=True)
    title_pt = models.CharField("title (Portuguese)", max_length=255, blank=True)
    body_pt = models.TextField("body (Portuguese)", blank=True)
    title_nl = models.CharField("title (Dutch)", max_length=255, blank=True)
    body_nl = models.TextField("body (Dutch)", blank=True)
    title_zh = models.CharField("title (Chinese)", max_length=255, blank=True)
    body_zh = models.TextField("body (Chinese)", blank=True)
    featured_image = models.FileField("featured image", upload_to=article_featured_image_upload_path, blank=True, null=True)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.DRAFT)
    published_at = models.DateTimeField("published at", blank=True, null=True)
    view_count = models.PositiveIntegerField("view count", default=0)
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "article"
        verbose_name_plural = "articles"

    def __str__(self):
        return self.title

    @staticmethod
    def _normalized_text(value):
        return (value or "").strip()

    def _translated_value(self, base_name, language_code):
        field_name = translated_field_name(base_name, language_code)
        return self._normalized_text(getattr(self, field_name, ""))

    def has_language_content(self, language_code):
        language_code = normalize_language_code(language_code)
        if self.original_language == language_code:
            return bool(self._normalized_text(self.title) and self._normalized_text(self.body))
        return bool(self._translated_value("title", language_code) and self._translated_value("body", language_code))

    def get_language_title(self, language_code):
        language_code = normalize_language_code(language_code)
        if self.original_language == language_code:
            return self._normalized_text(self.title)
        return self._translated_value("title", language_code)

    def get_language_body(self, language_code):
        language_code = normalize_language_code(language_code)
        if self.original_language == language_code:
            return self._normalized_text(self.body)
        return self._translated_value("body", language_code)

    def is_visible_in_language(self, language_code):
        return self.has_language_content(language_code)

    def get_language_direction(self, language_code):
        return "rtl" if is_rtl_language(language_code) else "ltr"

    def get_meta_description(self, language_code):
        return Truncator(self.get_language_body(language_code)).chars(165)

    def prepare_for_language(self, language_code):
        self.public_language = normalize_language_code(language_code)
        self.public_title = self.get_language_title(self.public_language)
        self.public_body = self.get_language_body(self.public_language)
        self.public_content_direction = self.get_language_direction(self.public_language)
        self.public_meta_description = self.get_meta_description(self.public_language)
        return self

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED and self.published_at and self.published_at <= timezone.now()

    @property
    def like_count(self):
        annotated_value = getattr(self, "likes_count", None)
        if annotated_value is not None:
            return annotated_value
        return self.likes.count()

    def get_absolute_url(self):
        return reverse("blog:detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        base_slug = slugify(self.slug or self.title) or "article"
        slug = base_slug
        counter = 2
        while Article.objects.exclude(pk=self.pk).filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        self.slug = slug

        if self.status == self.Status.PUBLISHED and self.published_at is None:
            self.published_at = timezone.now()
        if self.status == self.Status.DRAFT:
            self.published_at = None
        super().save(*args, **kwargs)

    @classmethod
    def visible_in_language_q(cls, language_code):
        language_code = normalize_language_code(language_code)
        title_field = translated_field_name("title", language_code)
        body_field = translated_field_name("body", language_code)
        return Q(original_language=language_code) | (Q(**{f"{title_field}__gt": ""}) & Q(**{f"{body_field}__gt": ""}))

    @classmethod
    def public_search_q(cls, language_code, search_term):
        search_term = (search_term or "").strip()
        if not search_term:
            return Q()

        language_code = normalize_language_code(language_code)
        translated_title = translated_field_name("title", language_code)
        translated_body = translated_field_name("body", language_code)

        original_language_query = Q(original_language=language_code) & (
            Q(title__icontains=search_term) | Q(body__icontains=search_term)
        )
        translated_language_query = (
            Q(**{f"{translated_title}__gt": ""})
            & Q(**{f"{translated_body}__gt": ""})
            & (Q(**{f"{translated_title}__icontains": search_term}) | Q(**{f"{translated_body}__icontains": search_term}))
        )
        return original_language_query | translated_language_query


class ArticleLike(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="article_likes",
        verbose_name="user",
    )
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="likes",
        verbose_name="article",
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "article")
        verbose_name = "article like"
        verbose_name_plural = "article likes"

    def __str__(self):
        return f"{self.user} -> {self.article}"
