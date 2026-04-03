from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from core.languages import translation_field_names
from .models import Category, Favorite, Stocklot, StocklotDocument, StocklotImage, StocklotVideo


class StocklotImageInline(admin.TabularInline):
    model = StocklotImage
    extra = 1


class StocklotDocumentInline(admin.TabularInline):
    model = StocklotDocument
    extra = 1


class StocklotVideoInline(admin.TabularInline):
    model = StocklotVideo
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "parent", "slug", "is_active")
    list_filter = ("is_active", "parent")
    search_fields = ("name", "slug", "parent__name")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Stocklot)
class StocklotAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "original_language",
        "company",
        "category",
        "status",
        "is_admin_verified",
        "is_active",
        "price",
        "currency",
        "quantity",
        "updated_at",
    )
    list_filter = ("status", "is_admin_verified", "is_active", "condition", "currency", "category")
    search_fields = ("title", "slug", "company__name", "company__owner__email", *translation_field_names())
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    inlines = (StocklotImageInline, StocklotVideoInline, StocklotDocumentInline)
    fieldsets = (
        (_("Listing info"), {"fields": ("company", "category", "original_language", "title", "slug")}),
        (
            _("Stocklot details"),
            {
                "fields": (
                    "description",
                    "condition",
                    "quantity",
                    "moq",
                    "unit_type",
                    "price",
                    "currency",
                )
            },
        ),
        (
            _("Translations"),
            {
                "fields": translation_field_names(),
                "classes": ("collapse",),
            },
        ),
        (
            _("Location & status"),
            {"fields": ("location_country", "location_city", "status", "is_admin_verified", "is_active")},
        ),
        (_("Timestamps"), {"fields": ("created_at", "updated_at")}),
    )


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "stocklot", "created_at")
    list_filter = ("created_at",)
    search_fields = ("user__email", "stocklot__title")
    raw_id_fields = ("user", "stocklot")
