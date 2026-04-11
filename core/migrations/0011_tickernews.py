from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_dealtrigger_buyer_identity_revealed_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="TickerNews",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("is_active", models.BooleanField(default=True)),
                ("priority", models.IntegerField(default=0)),
                (
                    "news_type",
                    models.CharField(
                        choices=[("info", "Info"), ("update", "Update"), ("alert", "Alert")],
                        default="info",
                        max_length=10,
                    ),
                ),
                (
                    "audience",
                    models.CharField(
                        choices=[("all", "All users"), ("buyers", "Buyers"), ("sellers", "Sellers"), ("verified_users", "Verified users")],
                        default="all",
                        max_length=20,
                    ),
                ),
                ("start_at", models.DateTimeField(blank=True, null=True)),
                ("end_at", models.DateTimeField(blank=True, null=True)),
                ("link_url", models.URLField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "ordering": ["-priority", "-created_at"],
                "verbose_name": "Ticker news",
                "verbose_name_plural": "Ticker news",
            },
        ),
        migrations.CreateModel(
            name="TickerNewsTranslation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("language_code", models.CharField(max_length=5)),
                ("message", models.CharField(max_length=255)),
                (
                    "ticker_news",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="core.tickernews",
                    ),
                ),
            ],
            options={
                "verbose_name": "Ticker news translation",
                "verbose_name_plural": "Ticker news translations",
            },
        ),
        migrations.AlterUniqueTogether(
            name="tickernewstranslation",
            unique_together={("ticker_news", "language_code")},
        ),
    ]

