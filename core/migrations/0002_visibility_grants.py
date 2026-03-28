from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("companies", "0002_company_identity_status"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0001_visibility_grant"),
    ]

    operations = [
        migrations.CreateModel(
            name="BuyerVisibilityGrant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scope", models.CharField(choices=[("single", "Single company"), ("all", "All companies")], default="single", max_length=10, verbose_name="scope")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("revoked", "Revoked")], default="pending", max_length=20, verbose_name="status")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                ("buyer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="visibility_grants_buyer", to=settings.AUTH_USER_MODEL)),
                ("granted_by", models.ForeignKey(blank=True, limit_choices_to={"is_staff": True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="buyer_visibility_grants_given", to=settings.AUTH_USER_MODEL)),
                ("target_company", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="visibility_grants_targeted_by_buyer", to="companies.company")),
            ],
            options={
                "verbose_name": "buyer visibility grant",
                "verbose_name_plural": "buyer visibility grants",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="CompanyVisibilityGrant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("scope", models.CharField(choices=[("single", "Single buyer"), ("all", "All buyers")], default="single", max_length=10, verbose_name="scope")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("revoked", "Revoked")], default="pending", max_length=20, verbose_name="status")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                ("company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="visibility_grants_company", to="companies.company")),
                ("granted_by", models.ForeignKey(blank=True, limit_choices_to={"is_staff": True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="company_visibility_grants_given", to=settings.AUTH_USER_MODEL)),
                ("target_buyer", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="visibility_grants_targeted_by_company", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "company visibility grant",
                "verbose_name_plural": "company visibility grants",
                "ordering": ["-created_at"],
            },
        ),
    ]
