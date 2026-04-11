from django.db import migrations, models


def mark_existing_users_verified(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    User.objects.update(email_verified=True, is_active=True)


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0009_alter_user_preferred_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="email_verified",
            field=models.BooleanField(default=False, verbose_name="email verified"),
        ),
        migrations.AlterField(
            model_name="user",
            name="full_name",
            field=models.CharField(blank=True, max_length=255, verbose_name="full name"),
        ),
        migrations.RunPython(mark_existing_users_verified, migrations.RunPython.noop),
    ]
