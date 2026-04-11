from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_user_full_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="preferred_language",
            field=models.CharField(
                choices=[("ar", "Arabic"), ("en", "English")],
                default="ar",
                max_length=2,
                verbose_name="preferred language",
            ),
        ),
    ]
