from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_seed_cms_blocks"),
    ]

    operations = [
        migrations.AddField(
            model_name="cmsblock",
            name="text_tr",
            field=models.TextField(blank=True, verbose_name="text (Turkish)"),
        ),
        migrations.AddField(
            model_name="cmsblock",
            name="text_fa",
            field=models.TextField(blank=True, verbose_name="text (Farsi)"),
        ),
        migrations.AddField(
            model_name="cmsblock",
            name="text_fr",
            field=models.TextField(blank=True, verbose_name="text (French)"),
        ),
        migrations.AddField(
            model_name="cmsblock",
            name="text_es",
            field=models.TextField(blank=True, verbose_name="text (Spanish)"),
        ),
        migrations.AddField(
            model_name="cmsblock",
            name="text_pt",
            field=models.TextField(blank=True, verbose_name="text (Portuguese)"),
        ),
        migrations.AddField(
            model_name="cmsblock",
            name="text_nl",
            field=models.TextField(blank=True, verbose_name="text (Dutch)"),
        ),
        migrations.AddField(
            model_name="cmsblock",
            name="text_zh",
            field=models.TextField(blank=True, verbose_name="text (Chinese)"),
        ),
    ]
