from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ("companies", "0001_initial"),
        ("rfqs", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.DeleteModel(
            name="Quote",
        ),
        migrations.CreateModel(
            name="RFQConversation",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("buyer", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rfq_conversations_as_buyer", to=settings.AUTH_USER_MODEL, verbose_name="buyer")),
                ("rfq", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="conversations", to="rfqs.rfq", verbose_name="rfq")),
                ("seller_company", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rfq_conversations", to="companies.company", verbose_name="seller company")),
                ("seller_user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rfq_conversations_as_seller", to=settings.AUTH_USER_MODEL, verbose_name="seller user")),
            ],
            options={
                "verbose_name": "RFQ conversation",
                "verbose_name_plural": "RFQ conversations",
            },
        ),
        migrations.CreateModel(
            name="RFQMessage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("message", models.TextField(verbose_name="message")),
                ("price", models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True, verbose_name="price")),
                ("currency", models.CharField(blank=True, choices=[("EUR", "EUR"), ("USD", "USD")], default="EUR", max_length=10, verbose_name="currency")),
                ("moderation_status", models.CharField(choices=[("pending_review", "Pending review"), ("approved", "Approved"), ("rejected", "Rejected")], default="pending_review", max_length=20, verbose_name="moderation status")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="created at")),
                ("conversation", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="messages", to="rfqs.rfqconversation", verbose_name="conversation")),
                ("sender_company", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="rfq_messages", to="companies.company", verbose_name="sender company")),
                ("sender_user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="rfq_messages", to=settings.AUTH_USER_MODEL, verbose_name="sender user")),
            ],
            options={
                "verbose_name": "RFQ message",
                "verbose_name_plural": "RFQ messages",
                "ordering": ["created_at"],
            },
        ),
        migrations.AlterUniqueTogether(
            name="rfqconversation",
            unique_together={("rfq", "seller_company")},
        ),
    ]
