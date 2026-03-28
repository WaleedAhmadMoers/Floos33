from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("companies", "0002_company_identity_status"),
    ]

    operations = [
        migrations.CreateModel(
            name="VisibilityGrant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("reveal_type", models.CharField(choices=[("buyer_sees_seller", "Buyer can see seller/company"), ("seller_sees_buyer", "Seller/company can see buyer")], max_length=30, verbose_name="reveal type")),
                ("status", models.CharField(choices=[("pending", "Pending"), ("approved", "Approved"), ("revoked", "Revoked")], default="pending", max_length=20, verbose_name="status")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                ("granted_by", models.ForeignKey(blank=True, limit_choices_to={"is_staff": True}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="visibility_grants_given", to=settings.AUTH_USER_MODEL)),
                ("target_company", models.ForeignKey(blank=True, help_text="Seller/company whose identity may be revealed to a buyer.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="visibility_grants_as_target_company", to="companies.company")),
                ("target_user", models.ForeignKey(blank=True, help_text="Buyer whose identity may be revealed to a seller company.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="visibility_grants_as_target_user", to=settings.AUTH_USER_MODEL)),
                ("viewer_company", models.ForeignKey(blank=True, help_text="Seller company requesting to view buyer identity.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="visibility_grants_as_viewer", to="companies.company")),
                ("viewer_user", models.ForeignKey(blank=True, help_text="Buyer requesting to view seller/company identity.", null=True, on_delete=django.db.models.deletion.CASCADE, related_name="visibility_grants_as_viewer", to=settings.AUTH_USER_MODEL)),
            ],
            options={
                "verbose_name": "visibility grant",
                "verbose_name_plural": "visibility grants",
                "ordering": ["-created_at"],
            },
        ),
    ]
