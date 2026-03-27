from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    class PreferredLanguage(models.TextChoices):
        ARABIC = "ar", _("Arabic")
        ENGLISH = "en", _("English")

    email = models.EmailField(_("email address"), unique=True)
    full_name = models.CharField(_("full name"), max_length=255)
    preferred_language = models.CharField(
        _("preferred language"),
        max_length=2,
        choices=PreferredLanguage.choices,
        default=PreferredLanguage.ARABIC,
    )
    is_buyer = models.BooleanField(_("buyer access"), default=True)
    is_seller = models.BooleanField(_("seller access"), default=False)
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_("Designates whether this user should be treated as active."),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates whether the user can log into the admin site."),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    class Meta:
        ordering = ["id"]
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.full_name or self.email

    @property
    def account_type_label(self):
        if self.is_buyer and self.is_seller:
            return _("Buyer and seller")
        if self.is_seller:
            return _("Seller")
        return _("Buyer")

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
            return _("Unverified")
        return request.get_status_display()


class SellerVerificationRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", _("Pending")
        APPROVED = "approved", _("Approved")
        REJECTED = "rejected", _("Rejected")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="seller_verification_request",
        verbose_name=_("user"),
    )
    company_name = models.CharField(_("company name"), max_length=255)
    contact_person_name = models.CharField(_("contact person name"), max_length=255)
    phone_number = models.CharField(_("phone number"), max_length=50)
    company_email = models.EmailField(_("company email"))
    company_address = models.CharField(_("company address"), max_length=255)
    country = models.CharField(_("country"), max_length=120)
    city = models.CharField(_("city"), max_length=120)
    business_type = models.CharField(_("business type"), max_length=120)
    business_description = models.TextField(_("business description"))
    registration_number = models.CharField(_("registration number"), max_length=120, blank=True)
    vat_number = models.CharField(_("VAT or tax number"), max_length=120, blank=True)
    supporting_document = models.FileField(
        _("supporting document"),
        upload_to="seller_verification_documents/",
        blank=True,
        null=True,
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    review_notes = models.TextField(_("review notes"), blank=True)
    submitted_at = models.DateTimeField(_("submitted at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    reviewed_at = models.DateTimeField(_("reviewed at"), blank=True, null=True)

    class Meta:
        verbose_name = _("seller verification request")
        verbose_name_plural = _("seller verification requests")
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
        UNVERIFIED = "unverified", _("Unverified")
        PENDING = "pending", _("Pending")
        VERIFIED = "verified", _("Verified")
        REJECTED = "rejected", _("Rejected")

    class DocumentType(models.TextChoices):
        NATIONAL_ID = "national_id", _("National ID")
        PASSPORT = "passport", _("Passport")
        DRIVER_LICENSE = "driver_license", _("Driver license")
        RESIDENCE_PERMIT = "residence_permit", _("Residence permit")
        OTHER = "other", _("Other")

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="buyer_verification_request",
        verbose_name=_("user"),
    )
    legal_full_name = models.CharField(_("legal full name"), max_length=255)
    phone_number = models.CharField(_("phone number"), max_length=50)
    country = models.CharField(_("country"), max_length=120)
    city = models.CharField(_("city"), max_length=120)
    address = models.CharField(_("address"), max_length=255)
    identity_document_type = models.CharField(
        _("identity document type"),
        max_length=40,
        choices=DocumentType.choices,
    )
    identity_document = models.FileField(
        _("identity document"),
        upload_to="buyer_verification_documents/",
    )
    selfie_document = models.FileField(
        _("selfie or face photo"),
        upload_to="buyer_verification_selfies/",
        blank=True,
        null=True,
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    review_notes = models.TextField(_("review notes"), blank=True)
    submitted_at = models.DateTimeField(_("submitted at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    reviewed_at = models.DateTimeField(_("reviewed at"), blank=True, null=True)

    class Meta:
        verbose_name = _("buyer verification request")
        verbose_name_plural = _("buyer verification requests")
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
