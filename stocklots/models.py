from decimal import Decimal

from django.db import models
from django.template.defaultfilters import slugify
from django.urls import reverse

from companies.models import Company


class Category(models.Model):
    name = models.CharField("name", max_length=120)
    slug = models.SlugField("slug", max_length=140, unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        blank=True,
        null=True,
        verbose_name="parent category",
    )
    is_active = models.BooleanField("active", default=True)

    class Meta:
        ordering = ["parent__name", "name"]
        verbose_name = "category"
        verbose_name_plural = "categories"

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
        BRAND_NEW = "brand_new", "Brand New"
        OVERSTOCK = "overstock", "Overstock"
        SHELF_PULL = "shelf_pull", "Shelf Pull"
        CUSTOMER_RETURN = "customer_return", "Customer Return"
        A_GRADE = "a_grade_return", "A-Grade Return"
        B_GRADE = "b_grade_return", "B-Grade Return"
        C_GRADE = "c_grade_return", "C-Grade Return"
        MIXED_GRADE = "mixed_grade", "Mixed Grade"
        REFURBISHED = "refurbished", "Refurbished"
        USED = "used", "Used"
        UNTESTED = "untested", "Untested"
        SALVAGE = "salvage", "Salvage"
        AS_IS = "as_is", "As-Is"

    class UnitType(models.TextChoices):
        PIECE = "piece", "Piece"
        CARTON = "carton", "Carton"
        PALLET = "pallet", "Pallet"
        SET = "set", "Set"
        KG = "kg", "Kilogram"
        TON = "ton", "Ton"
        LOT = "lot", "Lot"
        TRUCKLOAD = "truckload", "Truckload"
        CONTAINER_20 = "container_20ft", "20ft Container"
        CONTAINER_40 = "container_40ft", "40ft Container"

    class Currency(models.TextChoices):
        USD = "USD", "US Dollar"
        EUR = "EUR", "Euro"

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PENDING_REVIEW = "pending_review", "Pending review"
        APPROVED = "approved", "Approved"
        REJECTED = "rejected", "Rejected"
        ARCHIVED = "archived", "Archived"

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="stocklots",
        verbose_name="company",
    )
    title = models.CharField("title", max_length=255)
    slug = models.SlugField("slug", max_length=280, unique=True, blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="stocklots",
        verbose_name="category",
    )
    description = models.TextField("description")
    condition = models.CharField("condition", max_length=30, choices=Condition.choices)
    quantity = models.PositiveIntegerField("quantity")
    moq = models.PositiveIntegerField("minimum order quantity")
    unit_type = models.CharField("unit type", max_length=20, choices=UnitType.choices, default=UnitType.PIECE)
    price = models.DecimalField("price", max_digits=12, decimal_places=2, default=Decimal("0.00"))
    currency = models.CharField("currency", max_length=3, choices=Currency.choices, default=Currency.USD)
    location_country = models.CharField("location country", max_length=120)
    location_city = models.CharField("location city", max_length=120)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.DRAFT)
    is_admin_verified = models.BooleanField("admin verified", default=False)
    is_active = models.BooleanField("active", default=True)
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "stocklot"
        verbose_name_plural = "stocklots"

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.is_active and self.status == self.Status.APPROVED

    def get_absolute_url(self):
        return reverse("stocklots:detail", kwargs={"slug": self.slug})

    def clean(self):
        super().clean()
        if self.moq and self.quantity and self.moq > self.quantity:
            from django.core.exceptions import ValidationError

            raise ValidationError({"moq": "Minimum order quantity cannot exceed available quantity."})

    def save(self, *args, **kwargs):
        base_slug = slugify(self.title) or "stocklot"
        slug = base_slug
        counter = 2

        while Stocklot.objects.exclude(pk=self.pk).filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        self.slug = slug
        super().save(*args, **kwargs)


def stocklot_media_upload_path(instance, filename):
    return f"stocklots/{instance.stocklot_id}/{filename}"


class StocklotImage(models.Model):
    stocklot = models.ForeignKey(
        Stocklot,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="stocklot",
    )
    file = models.FileField("image file", upload_to=stocklot_media_upload_path)
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "stocklot image"
        verbose_name_plural = "stocklot images"

    def __str__(self):
        return f"{self.stocklot.title} image"


class StocklotDocument(models.Model):
    class DocType(models.TextChoices):
        PDF = "pdf", "PDF"
        EXCEL = "excel", "Excel / CSV"
        OTHER = "other", "Other"

    stocklot = models.ForeignKey(
        Stocklot,
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="stocklot",
    )
    file = models.FileField("document file", upload_to=stocklot_media_upload_path)
    doc_type = models.CharField("document type", max_length=12, choices=DocType.choices, default=DocType.OTHER)
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "stocklot document"
        verbose_name_plural = "stocklot documents"

    def __str__(self):
        return f"{self.stocklot.title} document"


class StocklotVideo(models.Model):
    stocklot = models.ForeignKey(
        Stocklot,
        on_delete=models.CASCADE,
        related_name="videos",
        verbose_name="stocklot",
    )
    file = models.FileField("video file", upload_to=stocklot_media_upload_path)
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        ordering = ["id"]
        verbose_name = "stocklot video"
        verbose_name_plural = "stocklot videos"

    def __str__(self):
        return f"{self.stocklot.title} video"


class Favorite(models.Model):
    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="user",
    )
    stocklot = models.ForeignKey(
        Stocklot,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="stocklot",
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        unique_together = ("user", "stocklot")
        ordering = ["-created_at"]
        verbose_name = "favorite"
        verbose_name_plural = "favorites"

    def __str__(self):
        return f"{self.user} -> {self.stocklot}"
