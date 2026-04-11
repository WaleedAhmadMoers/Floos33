from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("inquiries", "0002_inquiry_admin_gate"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("companies", "0002_company_identity_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="InquiryReply",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.TextField(verbose_name="message")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                (
                    "inquiry",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="replies",
                        to="inquiries.inquiry",
                        verbose_name="inquiry",
                    ),
                ),
                (
                    "sender_company",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="sent_inquiry_replies",
                        to="companies.company",
                        verbose_name="sender company",
                    ),
                ),
                (
                    "sender_user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sent_inquiry_replies_user",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="sender user",
                    ),
                ),
            ],
            options={
                "verbose_name": "inquiry reply",
                "verbose_name_plural": "inquiry replies",
                "ordering": ["created_at"],
            },
        ),
    ]
