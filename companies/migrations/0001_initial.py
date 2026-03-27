from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Company",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255, verbose_name="name")),
                ("legal_name", models.CharField(blank=True, max_length=255, verbose_name="legal name")),
                ("description", models.TextField(verbose_name="description")),
                ("phone", models.CharField(max_length=50, verbose_name="phone")),
                ("email", models.EmailField(max_length=254, verbose_name="email")),
                ("country", models.CharField(max_length=120, verbose_name="country")),
                ("city", models.CharField(max_length=120, verbose_name="city")),
                ("address", models.CharField(max_length=255, verbose_name="address")),
                ("website", models.URLField(blank=True, verbose_name="website")),
                (
                    "registration_number",
                    models.CharField(blank=True, max_length=120, verbose_name="registration number"),
                ),
                ("vat_number", models.CharField(blank=True, max_length=120, verbose_name="VAT number")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                (
                    "owner",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="company",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="owner",
                    ),
                ),
            ],
            options={
                "verbose_name": "company",
                "verbose_name_plural": "companies",
                "ordering": ["name"],
            },
        ),
    ]
