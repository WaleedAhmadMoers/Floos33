from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stocklots", "0007_alter_stocklot_condition_alter_stocklot_currency_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="stocklot",
            name="is_admin_verified",
            field=models.BooleanField(default=False, verbose_name="admin verified"),
        ),
        migrations.AlterField(
            model_name="stocklot",
            name="status",
            field=models.CharField(
                choices=[
                    ("draft", "Draft"),
                    ("pending_review", "Pending review"),
                    ("approved", "Approved"),
                    ("rejected", "Rejected"),
                    ("archived", "Archived"),
                ],
                default="draft",
                max_length=20,
                verbose_name="status",
            ),
        ),
        migrations.RunSQL(
            """
            UPDATE stocklots_stocklot SET status='approved' WHERE status='published';
            """,
            reverse_sql="""
            UPDATE stocklots_stocklot SET status='published' WHERE status='approved';
            """,
        ),
    ]
