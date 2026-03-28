from django.db import migrations, models


def move_existing_to_pending(apps, schema_editor):
    Inquiry = apps.get_model("inquiries", "Inquiry")
    Inquiry.objects.all().update(status="pending_admin")


class Migration(migrations.Migration):
    dependencies = [
        ("inquiries", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="inquiry",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending_admin", "Pending admin review"),
                    ("approved", "Approved"),
                    ("replied", "Replied"),
                    ("closed", "Closed"),
                ],
                default="pending_admin",
                max_length=20,
                verbose_name="status",
            ),
        ),
        migrations.RunPython(move_existing_to_pending, migrations.RunPython.noop),
    ]
