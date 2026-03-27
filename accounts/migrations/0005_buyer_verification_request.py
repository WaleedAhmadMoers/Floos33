import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_user_roles_and_seller_request"),
    ]

    operations = [
        migrations.CreateModel(
            name="BuyerVerificationRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("legal_full_name", models.CharField(max_length=255, verbose_name="legal full name")),
                ("phone_number", models.CharField(max_length=50, verbose_name="phone number")),
                ("country", models.CharField(max_length=120, verbose_name="country")),
                ("city", models.CharField(max_length=120, verbose_name="city")),
                ("address", models.CharField(max_length=255, verbose_name="address")),
                (
                    "identity_document_type",
                    models.CharField(
                        choices=[
                            ("national_id", "National ID"),
                            ("passport", "Passport"),
                            ("driver_license", "Driver license"),
                            ("residence_permit", "Residence permit"),
                            ("other", "Other"),
                        ],
                        max_length=40,
                        verbose_name="identity document type",
                    ),
                ),
                ("identity_document", models.FileField(upload_to="buyer_verification_documents/", verbose_name="identity document")),
                (
                    "selfie_document",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="buyer_verification_selfies/",
                        verbose_name="selfie or face photo",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("unverified", "Unverified"),
                            ("pending", "Pending"),
                            ("verified", "Verified"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=20,
                        verbose_name="status",
                    ),
                ),
                ("review_notes", models.TextField(blank=True, verbose_name="review notes")),
                ("submitted_at", models.DateTimeField(auto_now_add=True, verbose_name="submitted at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="updated at")),
                ("reviewed_at", models.DateTimeField(blank=True, null=True, verbose_name="reviewed at")),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="buyer_verification_request",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user",
                    ),
                ),
            ],
            options={
                "verbose_name": "buyer verification request",
                "verbose_name_plural": "buyer verification requests",
                "ordering": ["-updated_at"],
            },
        ),
    ]
