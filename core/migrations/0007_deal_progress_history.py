from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_update_dealtrigger_statuses"),
    ]

    operations = [
        migrations.AddField(
            model_name="dealtrigger",
            name="progress_status",
            field=models.CharField(
                choices=[
                    ("not_started", "Not started"),
                    ("in_progress", "In progress"),
                    ("ready", "Ready"),
                    ("completed", "Completed"),
                ],
                default="not_started",
                max_length=20,
                verbose_name="progress",
            ),
        ),
        migrations.CreateModel(
            name="DealHistory",
            fields=[
                (
                    "id",
                    models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"),
                ),
                ("action", models.CharField(max_length=50, verbose_name="action")),
                ("note", models.TextField(blank=True, verbose_name="note")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                (
                    "actor",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="deal_actions",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="actor",
                    ),
                ),
                (
                    "deal",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="history",
                        to="core.dealtrigger",
                        verbose_name="deal",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"], "verbose_name": "deal history", "verbose_name_plural": "deal history"},
        ),
    ]
