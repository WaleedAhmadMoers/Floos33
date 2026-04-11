from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_seed_tickernews"),
    ]

    operations = [
        migrations.CreateModel(
            name="CMSBlock",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("key", models.CharField(max_length=100, unique=True, verbose_name="key")),
                ("text_en", models.TextField(blank=True, verbose_name="text (English)")),
                ("text_de", models.TextField(blank=True, verbose_name="text (German)")),
                ("text_ar", models.TextField(blank=True, verbose_name="text (Arabic)")),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
            ],
            options={
                "verbose_name": "CMS block",
                "verbose_name_plural": "CMS blocks",
                "ordering": ["key"],
            },
        ),
    ]
