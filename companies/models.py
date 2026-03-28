from django.conf import settings
from django.db import models


class Company(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company",
        verbose_name="owner",
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
        help_text="Controls whether this company's identity is visible to other users.",
    )
    name = models.CharField("name", max_length=255)
    legal_name = models.CharField("legal name", max_length=255, blank=True)
    description = models.TextField("description")
    phone = models.CharField("phone", max_length=50)
    email = models.EmailField("email")
    country = models.CharField("country", max_length=120)
    city = models.CharField("city", max_length=120)
    address = models.CharField("address", max_length=255)
    website = models.URLField("website", blank=True)
    registration_number = models.CharField("registration number", max_length=120, blank=True)
    vat_number = models.CharField("VAT number", max_length=120, blank=True)
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "company"
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name

    def display_name_for(self, viewer=None):
        if viewer and (viewer.is_staff or viewer.id == self.owner_id):
            return self.name
        if self.identity_status == self.IdentityStatus.REVEALED:
            return self.name
        return f"Seller ID #{2000 + self.id}"
