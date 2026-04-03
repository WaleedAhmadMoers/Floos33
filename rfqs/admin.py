from django.contrib import admin

from core.languages import translation_field_names
from rfqs.models import RFQ, RFQConversation, RFQMessage


@admin.register(RFQ)
class RFQAdmin(admin.ModelAdmin):
    list_display = ("title", "original_language", "buyer", "status", "category", "quantity", "unit_type", "created_at")
    list_filter = ("status", "category")
    search_fields = ("title", "description", "buyer__email", *translation_field_names())
    fieldsets = (
        ("RFQ", {"fields": ("buyer", "original_language", "title", "description", "category")}),
        (
            "Commercial details",
            {"fields": ("quantity", "unit_type", "target_price", "currency", "location_country", "location_city")},
        ),
        ("Visibility", {"fields": ("moderation_status", "status")}),
        ("Translations", {"fields": translation_field_names(), "classes": ("collapse",)}),
    )


@admin.register(RFQConversation)
class RFQConversationAdmin(admin.ModelAdmin):
    list_display = ("rfq", "buyer", "seller_company", "created_at")
    search_fields = ("rfq__title", "seller_company__name", "buyer__email")
    autocomplete_fields = ("rfq", "buyer", "seller_company", "seller_user")


@admin.register(RFQMessage)
class RFQMessageAdmin(admin.ModelAdmin):
    list_display = ("conversation", "sender_user", "moderation_status", "created_at")
    list_filter = ("moderation_status",)
    search_fields = ("conversation__rfq__title", "sender_user__email")
