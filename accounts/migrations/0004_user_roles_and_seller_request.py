import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0003_user_preferred_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="is_buyer",
            field=models.BooleanField(default=True, verbose_name="buyer access"),
        ),
        migrations.AddField(
            model_name="user",
            name="is_seller",
            field=models.BooleanField(default=False, verbose_name="seller access"),
        ),
        migrations.CreateModel(
            name="SellerVerificationRequest",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("company_name", models.CharField(max_length=255, verbose_name="company name")),
                ("contact_person_name", models.CharField(max_length=255, verbose_name="contact person name")),
                ("phone_number", models.CharField(max_length=50, verbose_name="phone number")),
                ("company_email", models.EmailField(max_length=254, verbose_name="company email")),
                ("company_address", models.CharField(max_length=255, verbose_name="company address")),
                ("country", models.CharField(max_length=120, verbose_name="country")),
                ("city", models.CharField(max_length=120, verbose_name="city")),
                ("business_type", models.CharField(max_length=120, verbose_name="business type")),
                ("business_description", models.TextField(verbose_name="business description")),
                ("registration_number", models.CharField(blank=True, max_length=120, verbose_name="registration number")),
                ("vat_number", models.CharField(blank=True, max_length=120, verbose_name="VAT or tax number")),
                (
                    "supporting_document",
                    models.FileField(blank=True, null=True, upload_to="seller_verification_documents/", verbose_name="supporting document"),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
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
                        related_name="seller_verification_request",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user",
                    ),
                ),
            ],
            options={
                "verbose_name": "seller verification request",
                "verbose_name_plural": "seller verification requests",
                "ordering": ["-updated_at"],
            },
        ),
    ]
