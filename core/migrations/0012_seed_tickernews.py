from django.db import migrations
from django.utils import timezone


def seed_ticker_news(apps, schema_editor):
    TickerNews = apps.get_model("core", "TickerNews")
    TickerNewsTranslation = apps.get_model("core", "TickerNewsTranslation")

    items = [
        {
            "news_type": "info",
            "audience": "all",
            "priority": 30,
            "translations": {
                "en": "Marketplace maintenance window on Sunday 02:00–03:00 UTC",
                "de": "Wartungsfenster am Sonntag 02:00–03:00 UTC",
                "ar": "صيانة المنصة يوم الأحد من 02:00 إلى 03:00 بالتوقيت العالمي",
            },
        },
        {
            "news_type": "update",
            "audience": "all",
            "priority": 20,
            "translations": {
                "en": "New industrial categories added: Metalworking, Construction, Printing",
                "de": "Neue Industriekategorien: Metallbearbeitung, Bau, Druck",
                "ar": "تمت إضافة فئات صناعية جديدة: تشغيل المعادن، البناء، الطباعة",
            },
        },
        {
            "news_type": "alert",
            "audience": "all",
            "priority": 10,
            "translations": {
                "en": "Identity reveal approvals now faster: admins online 09:00–18:00 CET",
                "de": "Identitätsfreigaben jetzt schneller: Admins online 09:00–18:00 CET",
                "ar": "الموافقة على كشف الهوية أسرع الآن: المشرفون متواجدون 09:00–18:00 بتوقيت وسط أوروبا",
            },
        },
    ]

    for data in items:
        news = TickerNews.objects.create(
            is_active=True,
            priority=data["priority"],
            news_type=data["news_type"],
            audience=data["audience"],
            start_at=None,
            end_at=None,
            link_url="",
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        for lang, msg in data["translations"].items():
            TickerNewsTranslation.objects.create(
                ticker_news=news,
                language_code=lang,
                message=msg,
            )


def unseed_ticker_news(apps, schema_editor):
    TickerNews = apps.get_model("core", "TickerNews")
    TickerNewsTranslation = apps.get_model("core", "TickerNewsTranslation")

    messages = [
        "Marketplace maintenance window on Sunday 02:00–03:00 UTC",
        "Wartungsfenster am Sonntag 02:00–03:00 UTC",
        "صيانة المنصة يوم الأحد من 02:00 إلى 03:00 بالتوقيت العالمي",
        "New industrial categories added: Metalworking, Construction, Printing",
        "Neue Industriekategorien: Metallbearbeitung, Bau, Druck",
        "تمت إضافة فئات صناعية جديدة: تشغيل المعادن، البناء، الطباعة",
        "Identity reveal approvals now faster: admins online 09:00–18:00 CET",
        "Identitätsfreigaben jetzt schneller: Admins online 09:00–18:00 CET",
        "الموافقة على كشف الهوية أسرع الآن: المشرفون متواجدون 09:00–18:00 بتوقيت وسط أوروبا",
    ]

    TickerNewsTranslation.objects.filter(message__in=messages).delete()
    TickerNews.objects.filter(priority__in=[30, 20, 10], link_url="").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_tickernews"),
    ]

    operations = [
        migrations.RunPython(seed_ticker_news, reverse_code=unseed_ticker_news),
    ]
