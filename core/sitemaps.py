from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from rfqs.models import RFQ
from stocklots.models import Stocklot


class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return ["core:home", "stocklots:list", "rfqs:list", "core:about", "core:contact"]

    def location(self, item):
        return reverse(item)


class StocklotSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Stocklot.objects.filter(status=Stocklot.Status.APPROVED, is_active=True).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at


class RFQSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return RFQ.objects.filter(
            status=RFQ.Status.OPEN,
            moderation_status=RFQ.ModerationStatus.APPROVED,
        ).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    "static": StaticViewSitemap,
    "stocklots": StocklotSitemap,
    "rfqs": RFQSitemap,
}
