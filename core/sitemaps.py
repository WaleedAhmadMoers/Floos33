from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils import timezone

from blog.models import Article
from core.languages import DEFAULT_LANGUAGE_CODE, SUPPORTED_LANGUAGE_CHOICES
from rfqs.models import RFQ
from stocklots.models import Stocklot


def _public_language_codes():
    return [code for code, _label in SUPPORTED_LANGUAGE_CHOICES]


def _language_query_suffix(language_code):
    if language_code == DEFAULT_LANGUAGE_CODE:
        return ""
    return f"?lang={language_code}"


class LanguageVariantSitemap(Sitemap):
    def location(self, item):
        base_path, language_code = self.get_item_parts(item)
        return f"{base_path}{_language_query_suffix(language_code)}"

    def lastmod(self, item):
        return None

    def get_item_parts(self, item):
        raise NotImplementedError


class StaticViewSitemap(LanguageVariantSitemap):
    priority = 0.8
    changefreq = "weekly"
    public_views = (
        "core:home",
        "stocklots:list",
        "rfqs:list",
        "blog:list",
        "core:about",
        "core:contact",
        "core:privacy",
        "core:terms",
        "core:impressum",
    )

    def items(self):
        return [
            (view_name, language_code)
            for view_name in self.public_views
            for language_code in _public_language_codes()
        ]

    def get_item_parts(self, item):
        view_name, language_code = item
        return reverse(view_name), language_code


class StocklotSitemap(LanguageVariantSitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        items = []
        queryset = Stocklot.objects.filter(status=Stocklot.Status.APPROVED, is_active=True).order_by("-updated_at")
        for stocklot in queryset:
            for language_code in _public_language_codes():
                if stocklot.is_visible_in_language(language_code):
                    items.append((stocklot, language_code))
        return items

    def get_item_parts(self, item):
        stocklot, language_code = item
        return stocklot.get_absolute_url(), language_code

    def lastmod(self, item):
        stocklot, _language_code = item
        return stocklot.updated_at


class RFQSitemap(LanguageVariantSitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        items = []
        queryset = RFQ.objects.filter(
            status=RFQ.Status.OPEN,
            moderation_status=RFQ.ModerationStatus.APPROVED,
        ).order_by("-updated_at")
        for rfq in queryset:
            for language_code in _public_language_codes():
                if rfq.is_visible_in_language(language_code):
                    items.append((rfq, language_code))
        return items

    def get_item_parts(self, item):
        rfq, language_code = item
        return rfq.get_absolute_url(), language_code

    def lastmod(self, item):
        rfq, _language_code = item
        return rfq.updated_at


class BlogPostSitemap(LanguageVariantSitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        items = []
        queryset = Article.objects.filter(
            status=Article.Status.PUBLISHED,
            published_at__isnull=False,
            published_at__lte=timezone.now(),
        ).order_by("-updated_at")
        for article in queryset:
            for language_code in _public_language_codes():
                if article.is_visible_in_language(language_code):
                    items.append((article, language_code))
        return items

    def get_item_parts(self, item):
        article, language_code = item
        return article.get_absolute_url(), language_code

    def lastmod(self, item):
        article, _language_code = item
        return article.updated_at


sitemaps = {
    "static": StaticViewSitemap,
    "stocklots": StocklotSitemap,
    "rfqs": RFQSitemap,
    "blog": BlogPostSitemap,
}
