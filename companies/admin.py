from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "identity_status", "email", "phone", "country", "city", "created_at")
    list_filter = ("identity_status", "country", "city", "created_at")
    search_fields = (
        "name",
        "legal_name",
        "owner__email",
        "owner__full_name",
        "registration_number",
        "vat_number",
    )
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Ownership", {"fields": ("owner", "created_at")}),
        (
            "Basic company details",
            {
                "fields": (
                    "name",
                    "legal_name",
                    "description",
                    "identity_status",
                )
            },
        ),
        (
            "Contact information",
            {
                "fields": (
                    "phone",
                    "email",
                    "country",
                    "city",
                    "address",
                    "website",
                )
            },
        ),
        (
            "Registration",
            {
                "fields": (
                    "registration_number",
                    "vat_number",
                )
            },
        ),
    )
