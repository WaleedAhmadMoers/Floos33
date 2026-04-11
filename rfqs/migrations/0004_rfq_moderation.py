from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("rfqs", "0003_alter_rfq_currency_alter_rfq_unit_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="rfq",
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
