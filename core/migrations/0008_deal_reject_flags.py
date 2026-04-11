from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0007_deal_progress_history"),
    ]

    operations = [
        migrations.AddField(
            model_name="dealtrigger",
            name="buyer_rejected",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="dealtrigger",
            name="seller_rejected",
            field=models.BooleanField(default=False),
        ),
    ]
