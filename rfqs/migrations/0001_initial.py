from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("stocklots", "0009_favorite"),
        ("companies", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="RFQ",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="title")),
                ("description", models.TextField(verbose_name="description")),
                ("quantity", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="quantity")),
                ("unit_type", models.CharField(choices=[("piece", "Piece"), ("carton", "Carton"), ("pallet", "Pallet"), ("set", "Set"), ("kilogram", "Kilogram"), ("ton", "Ton"), ("lot", "Lot"), ("truckload", "Truckload"), ("container_20", "20ft Container"), ("container_40", "40ft Container")], max_length=50, verbose_name="unit type")),
                ("target_price", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="target price")),
                ("currency", models.CharField(choices=[("EUR", "EUR"), ("USD", "USD")], default="EUR", max_length=10, verbose_name="currency")),
                ("location_country", models.CharField(max_length=120, verbose_name="country")),
                ("location_city", models.CharField(max_length=120, verbose_name="city")),
                ("status", models.CharField(choices=[("open", "Open"), ("closed", "Closed")], default="open", max_length=20, verbose_name="status")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                ("buyer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rfqs", to=settings.AUTH_USER_MODEL, verbose_name="buyer")),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="rfqs", to="stocklots.category", verbose_name="category")),
            ],
            options={
                "verbose_name": "RFQ",
                "verbose_name_plural": "RFQs",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Quote",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("price", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="price")),
                ("currency", models.CharField(choices=[("EUR", "EUR"), ("USD", "USD")], default="EUR", max_length=10, verbose_name="currency")),
                ("message", models.TextField(verbose_name="message")),
                ("status", models.CharField(choices=[("pending_review", "Pending review"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending_review", max_length=20, verbose_name="status")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("rfq", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="quotes", to="rfqs.rfq", verbose_name="rfq")),
                ("seller_company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rfq_quotes", to="companies.company", verbose_name="seller company")),
                ("seller_user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rfq_quotes", to=settings.AUTH_USER_MODEL, verbose_name="seller user")),
            ],
            options={
                "verbose_name": "quote",
                "verbose_name_plural": "quotes",
                "ordering": ["-created_at"],
            },
        ),
    ]
