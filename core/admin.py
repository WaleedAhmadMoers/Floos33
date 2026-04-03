from django.contrib import admin

from core.cms import cms_text_field_names
from core.models import (
    AboutCMSBlock,
    BuyerVisibilityGrant,
    CMSBlock,
    CompanyVisibilityGrant,
    ContactCMSBlock,
    DealHistory,
    DealTrigger,
    FooterCMSBlock,
    HomepageCMSBlock,
    ImpressumCMSBlock,
    Notification,
    PrivacyCMSBlock,
    SharedCMSBlock,
    SupportMessage,
    TermsCMSBlock,
    TickerNews,
    TickerNewsTranslation,
)
from core.utils.notifications import create_notification


class PageScopedCMSBlockAdmin(admin.ModelAdmin):
    page_code = None
    list_display = ("key_suffix", "key", "is_active", "updated_at")
    list_filter = ("is_active", "updated_at")
    search_fields = ("key", *cms_text_field_names())
    readonly_fields = ("updated_at",)
    ordering = ("key",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if self.page_code:
            queryset = queryset.filter(page=self.page_code)
        return queryset

    def get_fields(self, request, obj=None):
        return ("key", *cms_text_field_names(), "is_active", "updated_at")

    def save_model(self, request, obj, form, change):
        if self.page_code:
            obj.page = self.page_code
        super().save_model(request, obj, form, change)

    @admin.display(description="Block")
    def key_suffix(self, obj):
        return obj.key_suffix


@admin.register(HomepageCMSBlock)
class HomepageCMSBlockAdmin(PageScopedCMSBlockAdmin):
    page_code = CMSBlock.Page.HOME


@admin.register(AboutCMSBlock)
class AboutCMSBlockAdmin(PageScopedCMSBlockAdmin):
    page_code = CMSBlock.Page.ABOUT


@admin.register(ContactCMSBlock)
class ContactCMSBlockAdmin(PageScopedCMSBlockAdmin):
    page_code = CMSBlock.Page.CONTACT


@admin.register(PrivacyCMSBlock)
class PrivacyCMSBlockAdmin(PageScopedCMSBlockAdmin):
    page_code = CMSBlock.Page.PRIVACY


@admin.register(TermsCMSBlock)
class TermsCMSBlockAdmin(PageScopedCMSBlockAdmin):
    page_code = CMSBlock.Page.TERMS


@admin.register(ImpressumCMSBlock)
class ImpressumCMSBlockAdmin(PageScopedCMSBlockAdmin):
    page_code = CMSBlock.Page.IMPRESSUM


@admin.register(FooterCMSBlock)
class FooterCMSBlockAdmin(PageScopedCMSBlockAdmin):
    page_code = CMSBlock.Page.FOOTER


@admin.register(SharedCMSBlock)
class SharedCMSBlockAdmin(PageScopedCMSBlockAdmin):
    page_code = CMSBlock.Page.SHARED


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


@admin.register(SupportMessage)
class SupportMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("name", "email", "subject", "message")
    readonly_fields = ("created_at", "updated_at", "user")
    raw_id_fields = ("user",)
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


@admin.register(DealHistory)
class DealHistoryAdmin(admin.ModelAdmin):
    list_display = ("deal", "action", "note", "actor", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("note", "deal__id", "actor__email")
    raw_id_fields = ("deal", "actor")


class TickerNewsTranslationInline(admin.TabularInline):
    model = TickerNewsTranslation
    extra = 1
    fields = ("language_code", "message")
    min_num = 1
    max_num = 3


@admin.register(TickerNews)
class TickerNewsAdmin(admin.ModelAdmin):
    list_display = ("__str__", "is_active", "news_type", "audience", "priority", "start_at", "end_at")
    list_filter = ("is_active", "news_type", "audience")
    search_fields = ("translations__message",)
    ordering = ("-priority", "-created_at")
    inlines = [TickerNewsTranslationInline]
    fieldsets = (
        (None, {"fields": ("is_active", "news_type", "audience", "priority")}),
        ("Schedule", {"fields": ("start_at", "end_at")}),
        ("Link", {"fields": ("link_url",)}),
    )
