from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from core.languages import SUPPORTED_LANGUAGE_CHOICES

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField("email address", unique=True)
    full_name = models.CharField("full name", max_length=255, blank=True)
    email_verified = models.BooleanField("email verified", default=False)
    preferred_language = models.CharField(
        "preferred language",
        max_length=2,
        choices=SUPPORTED_LANGUAGE_CHOICES,
        default="en",
    )
    # Admin override trust flag
    is_verified_user = models.BooleanField(
        "verified user",
        default=False,
        help_text="Admin override: mark this account as trusted without full buyer/seller verification.",
    )
    verified_user_at = models.DateTimeField("verified at", blank=True, null=True)
    verified_user_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="verified_users",
        verbose_name="verified by",
    )
    verified_user_note = models.TextField("verification note", blank=True)
    is_buyer = models.BooleanField("buyer access", default=True)
    is_seller = models.BooleanField("seller access", default=False)
    is_active = models.BooleanField(
        "active",
        default=True,
        help_text="Designates whether this user should be treated as active.",
    )
    class IdentityStatus(models.TextChoices):
        HIDDEN = "hidden", "Hidden"
        REVEALED = "revealed", "Revealed"
        REJECTED = "rejected", "Rejected"

    identity_status = models.CharField(
        "identity visibility",
        max_length=20,
        choices=IdentityStatus.choices,
        default=IdentityStatus.HIDDEN,
        help_text="Controls whether this user's identity is visible to other users.",
    )
    is_staff = models.BooleanField(
        "staff status",
        default=False,
        help_text="Designates whether the user can log into the admin site.",
    )
    date_joined = models.DateTimeField("date joined", default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        ordering = ["id"]
        verbose_name = "user"
        verbose_name_plural = "users"

    def __str__(self):
        return self.full_name or self.email

    @property
    def account_type_label(self):
        if self.is_buyer and self.is_seller:
            return "Buyer and seller"
        if self.is_seller:
            return "Seller"
        return "Buyer"

    @property
    def verified_user_label(self):
        return "Verified user" if self.is_verified_user else "Not verified"

    @property
    def buyer_verification_status(self):
        request = getattr(self, "buyer_verification_request", None)
        if request is None:
            return BuyerVerificationRequest.Status.UNVERIFIED
        return request.status

    @property
    def buyer_verification_status_label(self):
        request = getattr(self, "buyer_verification_request", None)
        if request is None:
            return "Unverified"
        return request.get_status_display()

    def display_name_for(self, viewer=None, role_hint=None):
        """
        Return a privacy-safe name for display to the given viewer.
        """
        if viewer and (viewer.is_staff or viewer.id == self.id):
            return self.full_name or self.email
        if self.identity_status == self.IdentityStatus.REVEALED:
            return self.full_name or self.email
        # Masked fallback
        role_label = "User"
        if role_hint == "seller":
            role_label = "Seller"
        elif role_hint == "buyer":
            role_label = "Buyer"
        return f"{role_label} ID #{1000 + self.id}"


class SellerVerificationRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="seller_verification_request",
        verbose_name="user",
    )
    company_name = models.CharField("company name", max_length=255)
    contact_person_name = models.CharField("contact person name", max_length=255)
    phone_number = models.CharField("phone number", max_length=50)
    company_email = models.EmailField("company email")
    company_address = models.CharField("company address", max_length=255)
    country = models.CharField("country", max_length=120)
    city = models.CharField("city", max_length=120)
    business_type = models.CharField("business type", max_length=120)
    business_description = models.TextField("business description")
    registration_number = models.CharField("registration number", max_length=120, blank=True)
    vat_number = models.CharField("VAT or tax number", max_length=120, blank=True)
    supporting_document = models.FileField(
        "supporting document",
        upload_to="seller_verification_documents/",
        blank=True,
        null=True,
    )
    status = models.CharField(
        "status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    review_notes = models.TextField("review notes", blank=True)
    submitted_at = models.DateTimeField("submitted at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)
    reviewed_at = models.DateTimeField("reviewed at", blank=True, null=True)

    class Meta:
        verbose_name = "seller verification request"
        verbose_name_plural = "seller verification requests"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.company_name} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            previous_status = (
                SellerVerificationRequest.objects.filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )

        if self.status == self.Status.PENDING:
            self.reviewed_at = None
        elif self.reviewed_at is None or previous_status != self.status:
            self.reviewed_at = timezone.now()

        super().save(*args, **kwargs)

        desired_seller_access = self.status == self.Status.APPROVED
        if self.user.is_seller != desired_seller_access:
            User.objects.filter(pk=self.user_id).update(is_seller=desired_seller_access)
            self.user.is_seller = desired_seller_access


class BuyerVerificationRequest(models.Model):
    class Status(models.TextChoices):
        UNVERIFIED = "unverified", "Unverified"
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    class DocumentType(models.TextChoices):
        NATIONAL_ID = "national_id", "National ID"
        PASSPORT = "passport", "Passport"
        DRIVER_LICENSE = "driver_license", "Driver license"
        RESIDENCE_PERMIT = "residence_permit", "Residence permit"
        OTHER = "other", "Other"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="buyer_verification_request",
        verbose_name="user",
    )
    legal_full_name = models.CharField("legal full name", max_length=255)
    phone_number = models.CharField("phone number", max_length=50)
    country = models.CharField("country", max_length=120)
    city = models.CharField("city", max_length=120)
    address = models.CharField("address", max_length=255)
    identity_document_type = models.CharField(
        "identity document type",
        max_length=40,
        choices=DocumentType.choices,
    )
    identity_document = models.FileField(
        "identity document",
        upload_to="buyer_verification_documents/",
    )
    selfie_document = models.FileField(
        "selfie or face photo",
        upload_to="buyer_verification_selfies/",
        blank=True,
        null=True,
    )
    status = models.CharField(
        "status",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    review_notes = models.TextField("review notes", blank=True)
    submitted_at = models.DateTimeField("submitted at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)
    reviewed_at = models.DateTimeField("reviewed at", blank=True, null=True)

    class Meta:
        verbose_name = "buyer verification request"
        verbose_name_plural = "buyer verification requests"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.legal_full_name} - {self.get_status_display()}"

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            previous_status = (
                BuyerVerificationRequest.objects.filter(pk=self.pk)
                .values_list("status", flat=True)
                .first()
            )

        if self.status == self.Status.PENDING:
            self.reviewed_at = None
        elif self.reviewed_at is None or previous_status != self.status:
            self.reviewed_at = timezone.now()

        super().save(*args, **kwargs)
