"""Root URL configuration for the floos33 backend project."""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import include, path

from core.sitemaps import sitemaps
from core.views import robots_txt

urlpatterns = [
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt, name="robots"),
    path("", include("accounts.urls")),
    path("", include("companies.urls")),
    path("stocklots/", include("stocklots.urls")),
    path("inquiries/", include("inquiries.urls")),
    path("rfqs/", include("rfqs.urls")),
    path("", include("core.urls")),
    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
