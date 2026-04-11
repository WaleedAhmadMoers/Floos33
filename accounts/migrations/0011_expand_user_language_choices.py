from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0010_user_email_verified_and_full_name_optional"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="preferred_language",
            field=models.CharField(
                choices=[
                    ("en", "English"),
                    ("de", "German"),
                    ("ar", "Arabic"),
                    ("tr", "Turkish"),
                    ("fa", "Farsi"),
                    ("fr", "French"),
                    ("es", "Spanish"),
                    ("pt", "Portuguese"),
                    ("nl", "Dutch"),
                    ("zh", "Chinese"),
                ],
                default="en",
                max_length=2,
                verbose_name="preferred language",
            ),
        ),
    ]
