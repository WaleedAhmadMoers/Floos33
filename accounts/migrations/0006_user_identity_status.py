from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0005_buyer_verification_request"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="identity_status",
            field=models.CharField(
                choices=[("hidden", "Hidden"), ("revealed", "Revealed"), ("rejected", "Rejected")],
                default="hidden",
                help_text="Controls whether this user's identity is visible to other users.",
                max_length=20,
                verbose_name="identity visibility",
            ),
        ),
    ]
