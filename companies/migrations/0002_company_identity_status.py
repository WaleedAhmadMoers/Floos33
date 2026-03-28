from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("companies", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="company",
            name="identity_status",
            field=models.CharField(
                choices=[("hidden", "Hidden"), ("revealed", "Revealed"), ("rejected", "Rejected")],
                default="hidden",
                help_text="Controls whether this company's identity is visible to other users.",
                max_length=20,
                verbose_name="identity visibility",
            ),
        ),
    ]
