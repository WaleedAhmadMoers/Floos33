from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("inquiries", "0003_inquiryreply"),
    ]

    operations = [
        migrations.AddField(
            model_name="inquiry",
            name="moderation_status",
            field=models.CharField(
                choices=[
                    ("pending_review", "Pending review"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                default="pending_review",
                max_length=20,
                verbose_name="moderation status",
            ),
        ),
        migrations.AddField(
            model_name="inquiryreply",
            name="moderation_status",
            field=models.CharField(
                choices=[
                    ("pending_review", "Pending review"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                ],
                default="pending_review",
                max_length=20,
                verbose_name="moderation status",
            ),
        ),
    ]
