from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0005_dealtrigger"),
    ]

    operations = [
        migrations.AlterField(
            model_name="dealtrigger",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("mutual_acceptance", "Mutual acceptance"),
                    ("approved", "Approved by admin"),
                    ("rejected", "Rejected by admin"),
                    ("cancelled", "Cancelled"),
                ],
                default="pending",
                max_length=20,
                verbose_name="status",
            ),
        ),
    ]
