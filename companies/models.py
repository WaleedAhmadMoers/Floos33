from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Company(models.Model):
    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="company",
        verbose_name=_("owner"),
    )
    name = models.CharField(_("name"), max_length=255)
    legal_name = models.CharField(_("legal name"), max_length=255, blank=True)
    description = models.TextField(_("description"))
    phone = models.CharField(_("phone"), max_length=50)
    email = models.EmailField(_("email"))
    country = models.CharField(_("country"), max_length=120)
    city = models.CharField(_("city"), max_length=120)
    address = models.CharField(_("address"), max_length=255)
    website = models.URLField(_("website"), blank=True)
    registration_number = models.CharField(_("registration number"), max_length=120, blank=True)
    vat_number = models.CharField(_("VAT number"), max_length=120, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("company")
        verbose_name_plural = _("companies")

    def __str__(self):
        return self.name
