from decimal import Decimal

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from companies.models import Company


class Category(models.Model):
    name = models.CharField(_("name"), max_length=120)
    slug = models.SlugField(_("slug"), max_length=140, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True,
        verbose_name=_("parent category"),
    )
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ["parent__name", "name"]
        verbose_name = _("category")
        verbose_name_plural = _("categories")

    def __str__(self):
        return self.full_name

    @property
    def full_name(self):
        if self.parent:
            return f"{self.parent.name} / {self.name}"
        return self.name

    @property
    def is_root(self):
        return self.parent_id is None

    def get_descendant_ids(self):
        descendant_ids = []
        for child in self.children.filter(is_active=True):
            descendant_ids.append(child.id)
            descendant_ids.extend(child.get_descendant_ids())
        return descendant_ids


class Stocklot(models.Model):
    class Condition(models.TextChoices):
        NEW = "new", _("New")
        LIKE_NEW = "like_new", _("Like new")
        CUSTOMER_RETURN = "customer_return", _("Customer return")
        SHELF_PULL = "shelf_pull", _("Shelf pull")
        MIXED = "mixed", _("Mixed")
        USED = "used", _("Used")

    class UnitType(models.TextChoices):
        PIECE = "piece", _("Piece")
        CARTON = "carton", _("Carton")
        PALLET = "pallet", _("Pallet")
        SET = "set", _("Set")
        KG = "kg", _("Kilogram")
        LOT = "lot", _("Lot")

    class Currency(models.TextChoices):
        USD = "USD", _("US Dollar")
        EUR = "EUR", _("Euro")
        SAR = "SAR", _("Saudi Riyal")
        AED = "AED", _("UAE Dirham")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")
        ARCHIVED = "archived", _("Archived")

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="stocklots",
        verbose_name=_("company"),
    )
    title = models.CharField(_("title"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=280, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="stocklots",
        verbose_name=_("category"),
    )
    description = models.TextField(_("description"))
    condition = models.CharField(_("condition"), max_length=30, choices=Condition.choices)
    quantity = models.PositiveIntegerField(_("quantity"))
    moq = models.PositiveIntegerField(_("minimum order quantity"))
    unit_type = models.CharField(_("unit type"), max_length=20, choices=UnitType.choices, default=UnitType.PIECE)
    price = models.DecimalField(_("price"), max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField(_("currency"), max_length=3, choices=Currency.choices, default=Currency.USD)
    location_country = models.CharField(_("location country"), max_length=120)
    location_city = models.CharField(_("location city"), max_length=120)
    status = models.CharField(_("status"), max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_active = models.BooleanField(_("active"), default=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("stocklot")
        verbose_name_plural = _("stocklots")

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.is_active and self.status == self.Status.PUBLISHED

    def get_absolute_url(self):
        return reverse("stocklots:detail", kwargs={"slug": self.slug})

    def clean(self):
        super().clean()
        if self.moq and self.quantity and self.moq > self.quantity:
            from django.core.exceptions import ValidationError

            raise ValidationError({"moq": _("Minimum order quantity cannot exceed available quantity.")})

    def save(self, *args, **kwargs):
        base_slug = slugify(self.title) or "stocklot"
        slug = base_slug
        counter = 2

        while Stocklot.objects.exclude(pk=self.pk).filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        self.slug = slug
        super().save(*args, **kwargs)
