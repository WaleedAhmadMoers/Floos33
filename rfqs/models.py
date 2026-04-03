from django.conf import settings
from django.db import models

from companies.models import Company
from core.multilingual import TranslatableContentMixin
from stocklots.models import Category, Stocklot


class RFQ(TranslatableContentMixin, models.Model):
    class ModerationStatus(models.TextChoices):
        PENDING_REVIEW = "pending_review", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rfqs",
        verbose_name="buyer",
    )
    title = models.CharField("title", max_length=255)
    description = models.TextField("description")
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="rfqs",
        verbose_name="category",
    )
    quantity = models.DecimalField("quantity", max_digits=12, decimal_places=2)
    unit_type = models.CharField("unit type", max_length=50, choices=Stocklot.UnitType.choices)
    target_price = models.DecimalField("target price", max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField("currency", max_length=10, choices=Stocklot.Currency.choices, default=Stocklot.Currency.EUR)
    location_country = models.CharField("country", max_length=120)
    location_city = models.CharField("city", max_length=120)
    moderation_status = models.CharField(
        "moderation status",
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING_REVIEW,
    )
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "RFQ"
        verbose_name_plural = "RFQs"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("rfqs:detail", args=[self.pk])


class RFQConversation(models.Model):
    rfq = models.ForeignKey(RFQ, on_delete=models.CASCADE, related_name="conversations", verbose_name="rfq")
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rfq_conversations_as_buyer",
        verbose_name="buyer",
    )
    seller_company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="rfq_conversations",
        verbose_name="seller company",
    )
    seller_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rfq_conversations_as_seller",
        verbose_name="seller user",
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        verbose_name = "RFQ conversation"
        verbose_name_plural = "RFQ conversations"
        unique_together = ("rfq", "seller_company")

    def __str__(self):
        return f"Conversation on {self.rfq} - {self.seller_company}"

    def participants(self):
        return [self.buyer, self.seller_user]


class RFQMessage(models.Model):
    class ModerationStatus(models.TextChoices):
        PENDING_REVIEW = "pending_review", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    conversation = models.ForeignKey(
        RFQConversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="conversation",
    )
    sender_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rfq_messages",
        verbose_name="sender user",
    )
    sender_company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="rfq_messages",
        verbose_name="sender company",
        null=True,
        blank=True,
    )
    message = models.TextField("message")
    attachment = models.FileField(
        "attachment",
        upload_to="attachments/rfq_messages/",
        null=True,
        blank=True,
        help_text="Optional image or video file.",
    )
    price = models.DecimalField("price", max_digits=12, decimal_places=2, null=True, blank=True)
    currency = models.CharField(
        "currency",
        max_length=10,
        choices=Stocklot.Currency.choices,
        default=Stocklot.Currency.EUR,
        blank=True,
    )
    moderation_status = models.CharField(
        "moderation status",
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING_REVIEW,
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "RFQ message"
        verbose_name_plural = "RFQ messages"

    def __str__(self):
        return f"Message in {self.conversation} ({self.get_moderation_status_display()})"


class RFQFavorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saved_rfqs",
        verbose_name="user",
    )
    rfq = models.ForeignKey(
        RFQ,
        on_delete=models.CASCADE,
        related_name="saved_by",
        verbose_name="rfq",
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "rfq")
        verbose_name = "saved RFQ"
        verbose_name_plural = "saved RFQs"

    def __str__(self):
        return f"{self.user} -> {self.rfq}"
