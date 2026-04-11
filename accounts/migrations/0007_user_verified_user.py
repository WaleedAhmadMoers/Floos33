from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0006_user_identity_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_verified_user",
            field=models.BooleanField(
                default=False,
                help_text="Admin override: marks this account as a trusted verified user.",
                verbose_name="verified user",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="verified_user_at",
            field=models.DateTimeField(blank=True, null=True, verbose_name="verified at"),
        ),
        migrations.AddField(
            model_name="user",
            name="verified_user_by",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="verified_users",
                to=settings.AUTH_USER_MODEL,
                verbose_name="verified by",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="verified_user_note",
            field=models.TextField(blank=True, verbose_name="verification note"),
        ),
    ]
