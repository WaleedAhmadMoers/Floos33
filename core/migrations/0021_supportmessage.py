from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0020_fill_cms_home_languages"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="SupportMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="name")),
                ("email", models.EmailField(max_length=254, verbose_name="email")),
                ("phone", models.CharField(blank=True, max_length=50, verbose_name="phone")),
                ("subject", models.CharField(max_length=180, verbose_name="subject")),
                ("message", models.TextField(verbose_name="message")),
                (
                    "status",
                    models.CharField(
                        choices=[("new", "New"), ("handled", "Handled")],
                        default="new",
                        max_length=20,
                        verbose_name="status",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=models.deletion.SET_NULL,
                        related_name="support_messages",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "support message",
                "verbose_name_plural": "support messages",
                "ordering": ["-created_at"],
            },
        ),
    ]
