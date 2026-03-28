from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .forms import AdminUserChangeForm, AdminUserCreationForm
from .models import BuyerVerificationRequest, SellerVerificationRequest, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = AdminUserCreationForm
    form = AdminUserChangeForm
    model = User
    ordering = ("id",)
    readonly_fields = ("is_buyer", "is_seller", "date_joined", "last_login")
    list_display = (
        "email",
        "full_name",
        "preferred_language",
        "identity_status",
        "buyer_verification_status_display",
        "is_buyer",
        "is_seller",
        "is_staff",
        "is_active",
        "is_superuser",
    )
    list_filter = (
        "preferred_language",
        "identity_status",
        "is_buyer",
        "is_seller",
        "is_staff",
        "is_active",
        "is_superuser",
    )
    search_fields = ("email", "full_name")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("full_name", "preferred_language")}),
        ("Privacy", {"fields": ("identity_status",)}),
        ("Roles", {"fields": ("is_buyer", "is_seller")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Timestamps", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "full_name", "preferred_language", "password1", "password2", "is_active", "is_staff"),
            },
        ),
    )
    filter_horizontal = ("groups", "user_permissions")

    @admin.display(description="Buyer verification status")
    def buyer_verification_status_display(self, obj):
        return obj.buyer_verification_status_label


@admin.register(SellerVerificationRequest)
class SellerVerificationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "company_name",
        "contact_person_name",
        "country",
        "city",
        "status",
        "submitted_at",
        "reviewed_at",
    )
    list_filter = ("status", "country", "city", "submitted_at")
    search_fields = ("user__email", "user__full_name", "company_name", "company_email", "registration_number", "vat_number")
    readonly_fields = ("submitted_at", "updated_at", "reviewed_at")
    fieldsets = (
        ("Request", {"fields": ("user", "status", "review_notes")}),
        (
            "Company details",
            {
                "fields": (
                    "company_name",
                    "contact_person_name",
                    "phone_number",
                    "company_email",
                    "company_address",
                    "country",
                    "city",
                    "business_type",
                    "business_description",
                    "registration_number",
                    "vat_number",
                    "supporting_document",
                )
            },
        ),
        ("Timestamps", {"fields": ("submitted_at", "updated_at", "reviewed_at")}),
    )


@admin.register(BuyerVerificationRequest)
class BuyerVerificationRequestAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "legal_full_name",
        "country",
        "city",
        "identity_document_type",
        "status",
        "submitted_at",
        "reviewed_at",
    )
    list_filter = ("status", "identity_document_type", "country", "city", "submitted_at")
    search_fields = ("user__email", "user__full_name", "legal_full_name", "phone_number")
    readonly_fields = ("submitted_at", "updated_at", "reviewed_at")
    fieldsets = (
        ("Request", {"fields": ("user", "status", "review_notes")}),
        (
            "Buyer details",
            {
                "fields": (
                    "legal_full_name",
                    "phone_number",
                    "country",
                    "city",
                    "address",
                    "identity_document_type",
                    "identity_document",
                    "selfie_document",
                )
            },
        ),
        ("Timestamps", {"fields": ("submitted_at", "updated_at", "reviewed_at")}),
    )
