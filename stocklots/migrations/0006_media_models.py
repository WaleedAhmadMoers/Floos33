from django.db import migrations, models
import stocklots.models


class Migration(migrations.Migration):
    dependencies = [
        ("stocklots", "0005_bazar_and_unit_cleanup"),
    ]

    operations = [
        migrations.CreateModel(
            name="StocklotImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to=stocklots.models.stocklot_media_upload_path, verbose_name="image file")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                (
                    "stocklot",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="images",
                        to="stocklots.stocklot",
                        verbose_name="stocklot",
                    ),
                ),
            ],
            options={
                "verbose_name": "stocklot image",
                "verbose_name_plural": "stocklot images",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="StocklotVideo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to=stocklots.models.stocklot_media_upload_path, verbose_name="video file")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                (
                    "stocklot",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="videos",
                        to="stocklots.stocklot",
                        verbose_name="stocklot",
                    ),
                ),
            ],
            options={
                "verbose_name": "stocklot video",
                "verbose_name_plural": "stocklot videos",
                "ordering": ["id"],
            },
        ),
        migrations.CreateModel(
            name="StocklotDocument",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("file", models.FileField(upload_to=stocklots.models.stocklot_media_upload_path, verbose_name="document file")),
                (
                    "doc_type",
                    models.CharField(
                        choices=[("pdf", "PDF"), ("excel", "Excel / CSV"), ("other", "Other")],
                        default="other",
                        max_length=12,
                        verbose_name="document type",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                (
                    "stocklot",
                    models.ForeignKey(
                        on_delete=models.deletion.CASCADE,
                        related_name="documents",
                        to="stocklots.stocklot",
                        verbose_name="stocklot",
                    ),
                ),
            ],
            options={
                "verbose_name": "stocklot document",
                "verbose_name_plural": "stocklot documents",
                "ordering": ["id"],
            },
        ),
    ]
