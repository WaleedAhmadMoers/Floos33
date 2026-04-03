from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("rfqs", "0006_rfqfavorite"),
    ]

    operations = [
        migrations.AddField(
            model_name="rfq",
            name="description_ar",
            field=models.TextField(blank=True, verbose_name="description (Arabic)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="description_de",
            field=models.TextField(blank=True, verbose_name="description (German)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="description_en",
            field=models.TextField(blank=True, verbose_name="description (English)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="description_es",
            field=models.TextField(blank=True, verbose_name="description (Spanish)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="description_fa",
            field=models.TextField(blank=True, verbose_name="description (Farsi)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="description_fr",
            field=models.TextField(blank=True, verbose_name="description (French)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="description_nl",
            field=models.TextField(blank=True, verbose_name="description (Dutch)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="description_pt",
            field=models.TextField(blank=True, verbose_name="description (Portuguese)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="description_tr",
            field=models.TextField(blank=True, verbose_name="description (Turkish)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="description_zh",
            field=models.TextField(blank=True, verbose_name="description (Chinese)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="original_language",
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
                verbose_name="original language",
            ),
        ),
        migrations.AddField(
            model_name="rfq",
            name="title_ar",
            field=models.CharField(blank=True, max_length=255, verbose_name="title (Arabic)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="title_de",
            field=models.CharField(blank=True, max_length=255, verbose_name="title (German)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="title_en",
            field=models.CharField(blank=True, max_length=255, verbose_name="title (English)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="title_es",
            field=models.CharField(blank=True, max_length=255, verbose_name="title (Spanish)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="title_fa",
            field=models.CharField(blank=True, max_length=255, verbose_name="title (Farsi)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="title_fr",
            field=models.CharField(blank=True, max_length=255, verbose_name="title (French)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="title_nl",
            field=models.CharField(blank=True, max_length=255, verbose_name="title (Dutch)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="title_pt",
            field=models.CharField(blank=True, max_length=255, verbose_name="title (Portuguese)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="title_tr",
            field=models.CharField(blank=True, max_length=255, verbose_name="title (Turkish)"),
        ),
        migrations.AddField(
            model_name="rfq",
            name="title_zh",
            field=models.CharField(blank=True, max_length=255, verbose_name="title (Chinese)"),
        ),
    ]
