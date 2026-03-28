from django.conf import settings
from django.db import models


class BuyerVisibilityGrant(models.Model):
    class Scope(models.TextChoices):
        SINGLE = "single", "Single company"
        ALL = "all", "All companies"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REVOKED = "revoked", "Revoked"

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="visibility_grants_buyer",
    )
    target_company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="visibility_grants_targeted_by_buyer",
        null=True,
        blank=True,
    )
    scope = models.CharField("scope", max_length=10, choices=Scope.choices, default=Scope.SINGLE)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.PENDING)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="buyer_visibility_grants_given",
        null=True,
        blank=True,
        limit_choices_to={"is_staff": True},
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "buyer visibility grant"
        verbose_name_plural = "buyer visibility grants"

    def __str__(self):
        return f"{self.buyer} -> {self.target_company or self.scope}"


class CompanyVisibilityGrant(models.Model):
    class Scope(models.TextChoices):
        SINGLE = "single", "Single buyer"
        ALL = "all", "All buyers"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REVOKED = "revoked", "Revoked"

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="visibility_grants_company",
    )
    target_buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="visibility_grants_targeted_by_company",
        null=True,
        blank=True,
    )
    scope = models.CharField("scope", max_length=10, choices=Scope.choices, default=Scope.SINGLE)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.PENDING)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="company_visibility_grants_given",
        null=True,
        blank=True,
        limit_choices_to={"is_staff": True},
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "company visibility grant"
        verbose_name_plural = "company visibility grants"

    def __str__(self):
        return f"{self.company} -> {self.target_buyer or self.scope}"


class Notification(models.Model):
    class Type(models.TextChoices):
        INQUIRY_NEW = "inquiry_new", "Inquiry new"
        INQUIRY_REPLY = "inquiry_reply", "Inquiry reply"
        RFQ_NEW_RESPONSE = "rfq_new_response", "RFQ new response"
        LISTING_APPROVED = "listing_approved", "Listing approved"
        RFQ_APPROVED = "rfq_approved", "RFQ approved"
        IDENTITY_REVEALED = "identity_revealed", "Identity revealed"
        DEAL_UPDATED = "deal_updated", "Deal updated"
        SYSTEM = "system", "System"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="recipient",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notifications_actor",
        verbose_name="actor",
    )
    notification_type = models.CharField("type", max_length=50, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField("title", max_length=255)
    body = models.TextField("body")
    url = models.CharField("url", max_length=500, blank=True)
    is_read = models.BooleanField("read", default=False)
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "notification"
        verbose_name_plural = "notifications"

    def __str__(self):
        return f"{self.notification_type} -> {self.recipient}"


class DealTrigger(models.Model):
    class DealType(models.TextChoices):
        INQUIRY = "inquiry", "Inquiry"
        RFQ = "rfq", "RFQ"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        MUTUAL = "mutual_acceptance", "Mutual acceptance"
        APPROVED = "approved", "Approved by admin"
        REJECTED = "rejected", "Rejected by admin"
        CANCELLED = "cancelled", "Cancelled"

    class Progress(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        IN_PROGRESS = "in_progress", "In progress"
        READY = "ready", "Ready"
        COMPLETED = "completed", "Completed"

    deal_type = models.CharField("deal type", max_length=20, choices=DealType.choices)
    inquiry = models.OneToOneField(
        "inquiries.Inquiry",
        on_delete=models.CASCADE,
        related_name="deal_trigger",
        null=True,
        blank=True,
    )
    rfq_conversation = models.OneToOneField(
        "rfqs.RFQConversation",
        on_delete=models.CASCADE,
        related_name="deal_trigger",
        null=True,
        blank=True,
    )
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deals_as_buyer")
    seller_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deals_as_seller", null=True, blank=True
    )
    seller_company = models.ForeignKey(
        "companies.Company", on_delete=models.CASCADE, related_name="deals", null=True, blank=True
    )
    buyer_accepted = models.BooleanField(default=False)
    seller_accepted = models.BooleanField(default=False)
    buyer_rejected = models.BooleanField(default=False)
    seller_rejected = models.BooleanField(default=False)
    buyer_identity_revealed = models.BooleanField(default=False)
    seller_identity_revealed = models.BooleanField(default=False)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.PENDING)
    progress_status = models.CharField(
        "progress",
        max_length=20,
        choices=Progress.choices,
        default=Progress.NOT_STARTED,
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="deal_acceptor"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "deal trigger"
        verbose_name_plural = "deal triggers"

    def __str__(self):
        target = self.inquiry or self.rfq_conversation
        return f"{self.deal_type} deal for {target}"


class DealHistory(models.Model):
    deal = models.ForeignKey(DealTrigger, on_delete=models.CASCADE, related_name="history", verbose_name="deal")
    action = models.CharField("action", max_length=50)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="deal_actions", verbose_name="actor"
    )
    note = models.TextField("note", blank=True)
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "deal history"
        verbose_name_plural = "deal history"

    def __str__(self):
        return f"{self.deal_id}: {self.action}"
