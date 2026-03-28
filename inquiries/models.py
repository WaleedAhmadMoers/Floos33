from django.conf import settings
from django.db import models

from companies.models import Company
from stocklots.models import Stocklot


class Inquiry(models.Model):
    class ModerationStatus(models.TextChoices):
        PENDING_REVIEW = "pending_review", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    class Status(models.TextChoices):
        PENDING_ADMIN = "pending_admin", "Pending admin review"
        APPROVED = "approved", "Approved"
        REPLIED = "replied", "Replied"
        CLOSED = "closed", "Closed"

    stocklot = models.ForeignKey(
        Stocklot,
        on_delete=models.CASCADE,
        related_name="inquiries",
        verbose_name="stocklot",
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_inquiries",
        verbose_name="buyer",
    )
    seller_company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="received_inquiries",
        verbose_name="seller company",
    )
    subject = models.CharField("subject", max_length=255, blank=True)
    message = models.TextField("message")
    status = models.CharField(
        "status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING_ADMIN,
    )
    moderation_status = models.CharField(
        "moderation status",
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING_REVIEW,
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "inquiry"
        verbose_name_plural = "inquiries"

    def __str__(self):
        return self.subject or f"Inquiry for {self.stocklot.title}"

    @property
    def display_subject(self):
        return self.subject or f"Inquiry about {self.stocklot.title}"


class InquiryReply(models.Model):
    class ModerationStatus(models.TextChoices):
        PENDING_REVIEW = "pending_review", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    inquiry = models.ForeignKey(
        Inquiry,
        on_delete=models.CASCADE,
        related_name="replies",
        verbose_name="inquiry",
    )
    sender_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_inquiry_replies_user",
        verbose_name="sender user",
    )
    sender_company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        related_name="sent_inquiry_replies",
        verbose_name="sender company",
        null=True,
        blank=True,
    )
    message = models.TextField("message")
    created_at = models.DateTimeField("created at", auto_now_add=True)
    moderation_status = models.CharField(
        "moderation status",
        max_length=20,
        choices=ModerationStatus.choices,
        default=ModerationStatus.PENDING_REVIEW,
    )

    class Meta:
        ordering = ["created_at"]
        verbose_name = "inquiry reply"
        verbose_name_plural = "inquiry replies"

    def __str__(self):
        return f"Reply on {self.inquiry_id} by {self.sender_user}"
