from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("companies", "0001_initial"),
        ("stocklots", "0006_media_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="Inquiry",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("subject", models.CharField(blank=True, max_length=255, verbose_name="subject")),
                ("message", models.TextField(verbose_name="message")),
                (
                    "status",
                    models.CharField(
                        choices=[("new", "New"), ("replied", "Replied"), ("closed", "Closed")],
                        default="new",
                        max_length=20,
                        verbose_name="status",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                (
                    "buyer",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_inquiries",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="buyer",
                    ),
                ),
                (
                    "seller_company",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="received_inquiries",
                        to="companies.company",
                        verbose_name="seller company",
                    ),
                ),
                (
                    "stocklot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="inquiries",
                        to="stocklots.stocklot",
                        verbose_name="stocklot",
                    ),
                ),
            ],
            options={
                "verbose_name": "inquiry",
                "verbose_name_plural": "inquiries",
                "ordering": ["-created_at"],
            },
        ),
    ]
