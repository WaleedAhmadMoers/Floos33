from django.conf import settings
from django.db import models


class CMSBlock(models.Model):
    class Page(models.TextChoices):
        HOME = "home", "Homepage"
        ABOUT = "about", "About"
        ACCOUNT = "account", "Account"
        BLOG = "blog", "Blog"
        CHAT = "chat", "Chat"
        CONTACT = "contact", "Contact"
        DASHBOARD = "dashboard", "Dashboard"
        DEAL = "deal", "Deals"
        INBOX = "inbox", "Inbox"
        LISTING_UI = "listing_ui", "Listing UI"
        NAV = "nav", "Navigation"
        NOTIFICATIONS = "notifications", "Notifications"
        PRIVACY = "privacy", "Privacy"
        RFQ_UI = "rfq_ui", "RFQ UI"
        SAVED = "saved", "Saved"
        SUPPORT = "support", "Support"
        TERMS = "terms", "Terms"
        IMPRESSUM = "impressum", "Impressum"
        FOOTER = "footer", "Footer"
        SHARED = "shared", "Shared / Global"

    page = models.CharField("page", max_length=20, choices=Page.choices, default=Page.SHARED)
    key = models.CharField("key", max_length=100, unique=True)
    text_en = models.TextField("text (English)", blank=True)
    text_de = models.TextField("text (German)", blank=True)
    text_ar = models.TextField("text (Arabic)", blank=True)
    text_tr = models.TextField("text (Turkish)", blank=True)
    text_fa = models.TextField("text (Farsi)", blank=True)
    text_fr = models.TextField("text (French)", blank=True)
    text_es = models.TextField("text (Spanish)", blank=True)
    text_pt = models.TextField("text (Portuguese)", blank=True)
    text_nl = models.TextField("text (Dutch)", blank=True)
    text_zh = models.TextField("text (Chinese)", blank=True)
    is_active = models.BooleanField("active", default=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        ordering = ["page", "key"]
        verbose_name = "CMS block"
        verbose_name_plural = "CMS blocks"

    def __str__(self):
        return self.key

    @property
    def key_suffix(self):
        if "." in self.key:
            return self.key.split(".", 1)[1]
        return self.key

    def save(self, *args, **kwargs):
        suffix = self.key.split(".", 1)[1] if "." in self.key else self.key
        self.key = f"{self.page}.{suffix}"
        super().save(*args, **kwargs)
        from core.cms import clear_cms_cache

        clear_cms_cache()

    def delete(self, *args, **kwargs):
        result = super().delete(*args, **kwargs)
        from core.cms import clear_cms_cache

        clear_cms_cache()
        return result


class HomepageCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS · Homepage"
        verbose_name_plural = "CMS · Homepage"


class AboutCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS · About"
        verbose_name_plural = "CMS · About"


class ContactCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS · Contact"
        verbose_name_plural = "CMS · Contact"


class PrivacyCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS · Privacy"
        verbose_name_plural = "CMS · Privacy"


class TermsCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS · Terms"
        verbose_name_plural = "CMS · Terms"


class ImpressumCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS · Impressum"
        verbose_name_plural = "CMS · Impressum"


class FooterCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS · Footer"
        verbose_name_plural = "CMS · Footer"


class SharedCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS · Shared / Global"
        verbose_name_plural = "CMS · Shared / Global"


class AccountCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - Account"
        verbose_name_plural = "CMS - Account"


class BlogCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - Blog"
        verbose_name_plural = "CMS - Blog"


class ChatCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - Chat"
        verbose_name_plural = "CMS - Chat"


class DashboardCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - Dashboard"
        verbose_name_plural = "CMS - Dashboard"


class DealCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - Deals"
        verbose_name_plural = "CMS - Deals"


class InboxCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - Inbox"
        verbose_name_plural = "CMS - Inbox"


class ListingUICMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - Listing UI"
        verbose_name_plural = "CMS - Listing UI"


class NavigationCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - Navigation"
        verbose_name_plural = "CMS - Navigation"


class NotificationsCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - Notifications"
        verbose_name_plural = "CMS - Notifications"


class RFQUICMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - RFQ UI"
        verbose_name_plural = "CMS - RFQ UI"


class SavedCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - Saved"
        verbose_name_plural = "CMS - Saved"


class SupportCMSBlock(CMSBlock):
    class Meta:
        proxy = True
        verbose_name = "CMS - Support"
        verbose_name_plural = "CMS - Support"


class SupportMessage(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        HANDLED = "handled", "Handled"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="support_messages",
        null=True,
        blank=True,
    )
    name = models.CharField("name", max_length=120)
    email = models.EmailField("email")
    phone = models.CharField("phone", max_length=50, blank=True)
    subject = models.CharField("subject", max_length=180)
    message = models.TextField("message")
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.NEW)
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "support message"
        verbose_name_plural = "support messages"

    def __str__(self):
        return f"{self.email} - {self.subject}"


class BuyerVisibilityGrant(models.Model):
    class Scope(models.TextChoices):
        SINGLE = "single", "Single company"
        ALL = "all", "All companies"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REVOKED = "revoked", "Revoked"

    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="visibility_grants_buyer",
    )
    target_company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="visibility_grants_targeted_by_buyer",
        null=True,
        blank=True,
    )
    scope = models.CharField("scope", max_length=10, choices=Scope.choices, default=Scope.SINGLE)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.PENDING)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="buyer_visibility_grants_given",
        null=True,
        blank=True,
        limit_choices_to={"is_staff": True},
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "buyer visibility grant"
        verbose_name_plural = "buyer visibility grants"

    def __str__(self):
        return f"{self.buyer} -> {self.target_company or self.scope}"


class CompanyVisibilityGrant(models.Model):
    class Scope(models.TextChoices):
        SINGLE = "single", "Single buyer"
        ALL = "all", "All buyers"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        APPROVED = "approved", "Approved"
        REVOKED = "revoked", "Revoked"

    company = models.ForeignKey(
        "companies.Company",
        on_delete=models.CASCADE,
        related_name="visibility_grants_company",
    )
    target_buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="visibility_grants_targeted_by_company",
        null=True,
        blank=True,
    )
    scope = models.CharField("scope", max_length=10, choices=Scope.choices, default=Scope.SINGLE)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.PENDING)
    granted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="company_visibility_grants_given",
        null=True,
        blank=True,
        limit_choices_to={"is_staff": True},
    )
    created_at = models.DateTimeField("created at", auto_now_add=True)
    updated_at = models.DateTimeField("updated at", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "company visibility grant"
        verbose_name_plural = "company visibility grants"

    def __str__(self):
        return f"{self.company} -> {self.target_buyer or self.scope}"


class Notification(models.Model):
    class Type(models.TextChoices):
        INQUIRY_NEW = "inquiry_new", "Inquiry new"
        INQUIRY_REPLY = "inquiry_reply", "Inquiry reply"
        RFQ_NEW_RESPONSE = "rfq_new_response", "RFQ new response"
        LISTING_APPROVED = "listing_approved", "Listing approved"
        RFQ_APPROVED = "rfq_approved", "RFQ approved"
        IDENTITY_REVEALED = "identity_revealed", "Identity revealed"
        DEAL_UPDATED = "deal_updated", "Deal updated"
        SYSTEM = "system", "System"

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="recipient",
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="notifications_actor",
        verbose_name="actor",
    )
    notification_type = models.CharField("type", max_length=50, choices=Type.choices, default=Type.SYSTEM)
    title = models.CharField("title", max_length=255)
    body = models.TextField("body")
    url = models.CharField("url", max_length=500, blank=True)
    is_read = models.BooleanField("read", default=False)
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "notification"
        verbose_name_plural = "notifications"

    def __str__(self):
        return f"{self.notification_type} -> {self.recipient}"


class DealTrigger(models.Model):
    class DealType(models.TextChoices):
        INQUIRY = "inquiry", "Inquiry"
        RFQ = "rfq", "RFQ"

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        MUTUAL = "mutual_acceptance", "Mutual acceptance"
        APPROVED = "approved", "Approved by admin"
        REJECTED = "rejected", "Rejected by admin"
        CANCELLED = "cancelled", "Cancelled"

    class Progress(models.TextChoices):
        NOT_STARTED = "not_started", "Not started"
        IN_PROGRESS = "in_progress", "In progress"
        READY = "ready", "Ready"
        COMPLETED = "completed", "Completed"

    deal_type = models.CharField("deal type", max_length=20, choices=DealType.choices)
    inquiry = models.OneToOneField(
        "inquiries.Inquiry",
        on_delete=models.CASCADE,
        related_name="deal_trigger",
        null=True,
        blank=True,
    )
    rfq_conversation = models.OneToOneField(
        "rfqs.RFQConversation",
        on_delete=models.CASCADE,
        related_name="deal_trigger",
        null=True,
        blank=True,
    )
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deals_as_buyer")
    seller_user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="deals_as_seller", null=True, blank=True
    )
    seller_company = models.ForeignKey(
        "companies.Company", on_delete=models.CASCADE, related_name="deals", null=True, blank=True
    )
    buyer_accepted = models.BooleanField(default=False)
    seller_accepted = models.BooleanField(default=False)
    buyer_rejected = models.BooleanField(default=False)
    seller_rejected = models.BooleanField(default=False)
    buyer_identity_revealed = models.BooleanField(default=False)
    seller_identity_revealed = models.BooleanField(default=False)
    status = models.CharField("status", max_length=20, choices=Status.choices, default=Status.PENDING)
    progress_status = models.CharField(
        "progress",
        max_length=20,
        choices=Progress.choices,
        default=Progress.NOT_STARTED,
    )
    accepted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="deal_acceptor"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "deal trigger"
        verbose_name_plural = "deal triggers"

    def __str__(self):
        target = self.inquiry or self.rfq_conversation
        return f"{self.deal_type} deal for {target}"


class DealHistory(models.Model):
    deal = models.ForeignKey(DealTrigger, on_delete=models.CASCADE, related_name="history", verbose_name="deal")
    action = models.CharField("action", max_length=50)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="deal_actions", verbose_name="actor"
    )
    note = models.TextField("note", blank=True)
    created_at = models.DateTimeField("created at", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "deal history"
        verbose_name_plural = "deal history"

    def __str__(self):
        return f"{self.deal_id}: {self.action}"


class TickerNews(models.Model):
    class NewsType(models.TextChoices):
        INFO = "info", "Info"
        UPDATE = "update", "Update"
        ALERT = "alert", "Alert"

    class Audience(models.TextChoices):
        ALL = "all", "All users"
        BUYERS = "buyers", "Buyers"
        SELLERS = "sellers", "Sellers"
        VERIFIED = "verified_users", "Verified users"

    is_active = models.BooleanField(default=True)
    priority = models.IntegerField(default=0)
    news_type = models.CharField(max_length=10, choices=NewsType.choices, default=NewsType.INFO)
    audience = models.CharField(max_length=20, choices=Audience.choices, default=Audience.ALL)
    start_at = models.DateTimeField(blank=True, null=True)
    end_at = models.DateTimeField(blank=True, null=True)
    link_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "-created_at"]
        verbose_name = "Ticker news"
        verbose_name_plural = "Ticker news"

    def __str__(self):
        return f"TickerNews #{self.pk} ({self.news_type})"


class TickerNewsTranslation(models.Model):
    ticker_news = models.ForeignKey(TickerNews, on_delete=models.CASCADE, related_name="translations")
    language_code = models.CharField(max_length=5)
    message = models.CharField(max_length=255)

    class Meta:
        unique_together = ("ticker_news", "language_code")
        verbose_name = "Ticker news translation"
        verbose_name_plural = "Ticker news translations"

    def __str__(self):
        return f"{self.ticker_news_id} [{self.language_code}]"
