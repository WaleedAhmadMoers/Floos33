from django.contrib import admin

from .models import Category, Stocklot


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
        "company",
        "category",
        "status",
        "is_active",
        "price",
        "currency",
        "quantity",
        "updated_at",
    )
    list_filter = ("status", "is_active", "condition", "currency", "category")
    search_fields = ("title", "slug", "company__name", "company__owner__email")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("الملكية", {"fields": ("company", "category", "title", "slug")}),
        (
            "تفاصيل العرض",
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
            "الموقع والحالة",
            {
                "fields": (
                    "location_country",
                    "location_city",
                    "status",
                    "is_active",
                )
            },
        ),
        ("التواريخ", {"fields": ("created_at", "updated_at")}),
    )
