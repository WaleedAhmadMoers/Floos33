from django.contrib import admin

from .models import Company


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "email", "phone", "country", "city", "created_at")
    list_filter = ("country", "city", "created_at")
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
        ("الحساب المرتبط", {"fields": ("owner", "created_at")}),
        (
            "البيانات الأساسية",
            {
                "fields": (
                    "name",
                    "legal_name",
                    "description",
                )
            },
        ),
        (
            "بيانات التواصل",
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
            "البيانات القانونية",
            {
                "fields": (
                    "registration_number",
                    "vat_number",
                )
            },
        ),
    )
