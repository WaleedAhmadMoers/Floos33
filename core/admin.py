from django.contrib import admin

from core.models import BuyerVisibilityGrant, CompanyVisibilityGrant, Notification, DealTrigger
from core.utils.notifications import create_notification


@admin.register(BuyerVisibilityGrant)
class BuyerVisibilityGrantAdmin(admin.ModelAdmin):
    list_display = ("buyer", "scope", "target_company", "status", "granted_by", "created_at")
    list_filter = ("scope", "status", "created_at")
    search_fields = ("buyer__email", "buyer__full_name", "target_company__name")
    raw_id_fields = ("buyer", "target_company", "granted_by")
    ordering = ("-created_at",)


@admin.register(CompanyVisibilityGrant)
class CompanyVisibilityGrantAdmin(admin.ModelAdmin):
    list_display = ("company", "scope", "target_buyer", "status", "granted_by", "created_at")
    list_filter = ("scope", "status", "created_at")
    search_fields = ("company__name", "company__owner__email", "target_buyer__email", "target_buyer__full_name")
    raw_id_fields = ("company", "target_buyer", "granted_by")
    ordering = ("-created_at",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("recipient", "notification_type", "title", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "created_at")
    search_fields = ("title", "body", "recipient__email")
    raw_id_fields = ("recipient", "actor")
    ordering = ("-created_at",)


@admin.register(DealTrigger)
class DealTriggerAdmin(admin.ModelAdmin):
    list_display = ("deal_type", "status", "inquiry", "rfq_conversation", "buyer", "seller_company", "created_at")
    list_filter = ("deal_type", "status", "created_at")
    search_fields = ("inquiry__subject", "rfq_conversation__rfq__title", "buyer__email", "seller_company__name")
    raw_id_fields = ("inquiry", "rfq_conversation", "buyer", "seller_user", "seller_company", "accepted_by")
    actions = ["approve_deals", "reject_deals"]

    def approve_deals(self, request, queryset):
        updated = queryset.update(status=DealTrigger.Status.APPROVED)
        for deal in queryset:
            url = ""
            try:
                url = deal.inquiry.get_absolute_url()
            except Exception:
                try:
                    url = deal.rfq_conversation and deal.rfq_conversation.rfq.get_absolute_url()
                except Exception:
                    url = ""
            for recipient in [deal.buyer, deal.seller_user]:
                if recipient:
                    create_notification(
                        recipient=recipient,
                        actor=request.user,
                        notification_type=Notification.Type.DEAL_UPDATED,
                        title="Deal approved by admin",
                        body="Admin approved your deal.",
                        url=url,
                    )
        self.message_user(request, f"{updated} deal(s) approved.")

    def reject_deals(self, request, queryset):
        updated = queryset.update(status=DealTrigger.Status.REJECTED)
        for deal in queryset:
            url = ""
            try:
                url = deal.inquiry.get_absolute_url()
            except Exception:
                try:
                    url = deal.rfq_conversation and deal.rfq_conversation.rfq.get_absolute_url()
                except Exception:
                    url = ""
            for recipient in [deal.buyer, deal.seller_user]:
                if recipient:
                    create_notification(
                        recipient=recipient,
                        actor=request.user,
                        notification_type=Notification.Type.DEAL_UPDATED,
                        title="Deal rejected by admin",
                        body="Admin rejected the deal.",
                        url=url,
                    )
        self.message_user(request, f"{updated} deal(s) rejected.")

    approve_deals.short_description = "Approve selected deals"
    reject_deals.short_description = "Reject selected deals"
