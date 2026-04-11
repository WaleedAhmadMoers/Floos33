from django.contrib import admin

from .models import Inquiry, InquiryReply


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("id", "stocklot", "buyer", "seller_company", "status", "moderation_status", "created_at")
    list_filter = ("status", "moderation_status", "seller_company")
    search_fields = ("subject", "message", "stocklot__title", "buyer__email", "seller_company__name")
    raw_id_fields = ("stocklot", "buyer", "seller_company")


@admin.register(InquiryReply)
class InquiryReplyAdmin(admin.ModelAdmin):
    list_display = ("inquiry", "sender_user", "sender_company", "moderation_status", "created_at")
    list_filter = ("moderation_status", "created_at")
    search_fields = ("inquiry__stocklot__title", "sender_user__email", "sender_company__name", "message")
    raw_id_fields = ("inquiry", "sender_user", "sender_company")
