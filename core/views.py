from django.contrib import messages
from django.db import models, transaction
from django.db.models import Exists, OuterRef, Value, BooleanField
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, View, DetailView, CreateView, UpdateView, DeleteView, FormView
from django.http import JsonResponse, HttpResponse
from django.utils.http import url_has_allowed_host_and_scheme
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from stocklots.models import Stocklot, Category
from stocklots.models import Favorite
from core.models import CMSBlock, Notification, DealTrigger, SupportMessage
from rfqs.models import RFQMessage, RFQ, RFQConversation, RFQFavorite
from inquiries.models import InquiryReply, Inquiry
from companies.models import Company
from accounts.models import User
from core.cms import get_cms_map, get_cms_text
from core.context_processors import resolve_site_language
from core.language_runtime import LANGUAGE_COOKIE_NAME, LANGUAGE_PREFERENCE_SOURCE_COOKIE
from core.language_runtime import LANGUAGE_PROMPT_DISMISSED_COOKIE, LANGUAGE_SOURCE_EXPLICIT
from core.language_runtime import detect_browser_language, remove_language_query_param
from core.languages import SUPPORTED_LANGUAGE_CODES
from core.multilingual import prepare_objects_for_language
from core.utils.notifications import create_notification
from core.utils.deals import _broadcast_deal, _identity_status
from core.utils.verification import enforce_verified
from core.models import BuyerVisibilityGrant, CompanyVisibilityGrant
from core import forms_admin
from core.forms import SupportContactForm
from core.models import DealHistory


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        language_code = resolve_site_language(self.request)
        cms = get_cms_map(language_code)
        public_stocklots = (
            Stocklot.objects.select_related("company", "company__owner", "category", "category__parent")
            .filter(status=Stocklot.Status.APPROVED, is_active=True)
            .filter(Stocklot.visible_in_language_q(language_code))
        )
        qs = (
            public_stocklots
            .annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(user=self.request.user, stocklot=OuterRef("pk"))
                ) if self.request.user.is_authenticated else Value(False, output_field=BooleanField())
            )
            .order_by("-created_at")
        )
        paginator = Paginator(qs, 6)
        page_num = self.request.GET.get("hp", 1)
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
        context["homepage_stocklots"] = prepare_objects_for_language(list(page_obj.object_list), language_code)
        # build prev/next links preserving other home params
        base_qs = self.request.GET.copy()
        base_qs.pop("hp", None)
        base_prefix = "?" + base_qs.urlencode()
        if base_prefix != "?" and not base_prefix.endswith("&"):
            base_prefix += "&"
        elif base_prefix == "?":
            base_prefix = "?"
        context["home_page_obj"] = page_obj
        context["home_page_prev"] = f"{base_prefix}hp={page_obj.previous_page_number()}" if page_obj.has_previous() else None
        context["home_page_next"] = f"{base_prefix}hp={page_obj.next_page_number()}" if page_obj.has_next() else None
        context["homepage_feed"] = prepare_objects_for_language(
            list(public_stocklots.select_related("company", "category").order_by("-updated_at")[:5]),
            language_code,
        )
        context["how_it_works_steps"] = [
            {
                "number": 1,
                "title": get_cms_text("home.how_step_1_title", language_code, cms),
                "description": get_cms_text("home.how_step_1_description", language_code, cms),
            },
            {
                "number": 2,
                "title": get_cms_text("home.how_step_2_title", language_code, cms),
                "description": get_cms_text("home.how_step_2_description", language_code, cms),
            },
            {
                "number": 3,
                "title": get_cms_text("home.how_step_3_title", language_code, cms),
                "description": get_cms_text("home.how_step_3_description", language_code, cms),
            },
            {
                "number": 4,
                "title": get_cms_text("home.how_step_4_title", language_code, cms),
                "description": get_cms_text("home.how_step_4_description", language_code, cms),
            },
        ]
        context["trust_safety_points"] = [
            {
                "title": get_cms_text("home.trust_point_1_title", language_code, cms),
                "description": get_cms_text("home.trust_point_1_description", language_code, cms),
            },
            {
                "title": get_cms_text("home.trust_point_2_title", language_code, cms),
                "description": get_cms_text("home.trust_point_2_description", language_code, cms),
            },
            {
                "title": get_cms_text("home.trust_point_3_title", language_code, cms),
                "description": get_cms_text("home.trust_point_3_description", language_code, cms),
            },
            {
                "title": get_cms_text("home.trust_point_4_title", language_code, cms),
                "description": get_cms_text("home.trust_point_4_description", language_code, cms),
            },
        ]
        context["recent_rfqs"] = prepare_objects_for_language(
            list(
                RFQ.objects.select_related("buyer", "category")
                .filter(moderation_status=RFQ.ModerationStatus.APPROVED, status=RFQ.Status.OPEN)
                .filter(RFQ.visible_in_language_q(language_code))
                .order_by("-created_at")[:3]
            ),
            language_code,
        )
        # simple ribbon metrics
        context["stats_ribbon"] = {
            "avg_deal_size": "EUR 12,450",
            "countries": public_stocklots
            .values_list("location_country", flat=True)
            .distinct()
            .count(),
            "active_listings": public_stocklots.count(),
            "open_deals": DealTrigger.objects.filter(status__in=[DealTrigger.Status.PENDING, DealTrigger.Status.MUTUAL]).count(),
        }
        # popular categories (by stock count)
        context["popular_categories"] = (
            Category.objects.filter(stocklots__in=public_stocklots)
            .annotate(cnt=models.Count("stocklots"))
            .order_by("-cnt")[:8]
        )
        return context


class CMSContentMixin:
    cms_namespace = CMSBlock.Page.SHARED

    def get_language_code(self):
        return resolve_site_language(self.request)

    def get_cms_blocks(self):
        return getattr(self.request, "_cms_blocks", None) or get_cms_map(self.get_language_code())

    def cms_text(self, key):
        scoped_key = key if "." in key else f"{self.cms_namespace}.{key}"
        return get_cms_text(scoped_key, self.get_language_code(), self.get_cms_blocks())

    def get_cms_sections(self, count):
        sections = []
        for index in range(1, count + 1):
            title = self.cms_text(f"section_{index}_title")
            body = self.cms_text(f"section_{index}_body")
            if title or body:
                sections.append({"title": title, "body": body})
        return sections


class CMSPageView(CMSContentMixin, TemplateView):
    template_name = "core/cms_page.html"
    section_count = 0

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_meta_title"] = self.cms_text("meta_title")
        context["page_meta_description"] = self.cms_text("meta_description")
        context["page_eyebrow"] = self.cms_text("eyebrow")
        context["page_title"] = self.cms_text("title")
        context["page_intro"] = self.cms_text("intro")
        context["page_sections"] = self.get_cms_sections(self.section_count)
        return context


class AboutView(CMSPageView):
    cms_namespace = CMSBlock.Page.ABOUT
    section_count = 3


class PrivacyView(CMSPageView):
    cms_namespace = CMSBlock.Page.PRIVACY
    section_count = 4


class TermsView(CMSPageView):
    cms_namespace = CMSBlock.Page.TERMS
    section_count = 4


class ImpressumView(CMSContentMixin, TemplateView):
    template_name = "core/impressum.html"
    cms_namespace = CMSBlock.Page.IMPRESSUM

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_meta_title"] = self.cms_text("meta_title")
        context["page_meta_description"] = self.cms_text("meta_description")
        context["page_eyebrow"] = self.cms_text("eyebrow")
        context["page_title"] = self.cms_text("title")
        context["page_intro"] = self.cms_text("intro")
        context["impressum_items"] = [
            {
                "label": self.cms_text("company_name_label"),
                "value": self.cms_text("company_name"),
            },
            {
                "label": self.cms_text("address_label"),
                "value": self.cms_text("address"),
            },
            {
                "label": self.cms_text("contact_label"),
                "value": self.cms_text("contact_body"),
            },
            {
                "label": self.cms_text("representative_label"),
                "value": self.cms_text("representative"),
            },
            {
                "label": self.cms_text("registration_label"),
                "value": self.cms_text("registration"),
            },
            {
                "label": self.cms_text("vat_label"),
                "value": self.cms_text("vat"),
            },
        ]
        context["legal_title"] = self.cms_text("legal_title")
        context["legal_body"] = self.cms_text("legal_body")
        return context


class ContactView(CMSContentMixin, FormView):
    template_name = "core/contact.html"
    form_class = SupportContactForm
    success_url = reverse_lazy("core:contact")
    cms_namespace = CMSBlock.Page.CONTACT

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        def cms_text_or_default(key, default=""):
            value = self.cms_text(key)
            return value or default

        kwargs["cms_text"] = cms_text_or_default
        return kwargs

    def get_support_whatsapp_url(self):
        digits = "".join(ch for ch in settings.SUPPORT_PHONE if ch.isdigit())
        return f"https://wa.me/{digits}"

    def get_initial(self):
        initial = super().get_initial()
        if self.request.user.is_authenticated:
            initial["name"] = self.request.user.full_name or ""
            initial["email"] = self.request.user.email or ""
            initial["phone"] = getattr(self.request.user, "phone", "") or ""
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["support_email"] = settings.SUPPORT_EMAIL
        context["support_phone"] = settings.SUPPORT_PHONE
        context["support_whatsapp_url"] = self.get_support_whatsapp_url()
        context["contact_help_topics"] = [
            self.cms_text("help_item_1"),
            self.cms_text("help_item_2"),
            self.cms_text("help_item_3"),
            self.cms_text("help_item_4"),
        ]
        return context

    def form_valid(self, form):
        support_email = settings.SUPPORT_EMAIL
        subject = (form.cleaned_data.get("subject") or "").strip() or self.cms_text("email_subject_fallback")
        support_message = form.save(commit=False)
        support_message.subject = subject
        if self.request.user.is_authenticated:
            support_message.user = self.request.user
        support_message.status = SupportMessage.Status.NEW
        support_message.save()
        message = (
            f"Support message ID: {support_message.pk}\n"
            f"Name: {support_message.name}\n"
            f"Email: {support_message.email}\n"
            f"Phone: {support_message.phone or '-'}\n"
            f"Subject: {support_message.subject}\n\n"
            f"{support_message.message}"
        )
        send_mail(
            subject=f"[floos33 Support] {subject}",
            message=message,
            from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@floos33.local"),
            recipient_list=[support_email],
            fail_silently=True,
        )
        messages.success(self.request, self.cms_text("success_message"))
        return redirect(self.get_success_url())


class SetLanguageView(View):
    cookie_max_age = 60 * 60 * 24 * 365

    def get_next_url(self, request):
        next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("core:home")
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            return reverse("core:home")
        return remove_language_query_param(next_url)

    def apply_language_preference(self, request, response, language):
        request.session["site_language"] = language
        response.set_cookie(LANGUAGE_COOKIE_NAME, language, max_age=self.cookie_max_age, samesite="Lax")
        response.set_cookie(
            LANGUAGE_PREFERENCE_SOURCE_COOKIE,
            LANGUAGE_SOURCE_EXPLICIT,
            max_age=self.cookie_max_age,
            samesite="Lax",
        )
        response.delete_cookie(LANGUAGE_PROMPT_DISMISSED_COOKIE)
        if request.user.is_authenticated and getattr(request.user, "preferred_language", None) != language:
            request.user.preferred_language = language
            request.user.save(update_fields=["preferred_language"])

    def post(self, request, *args, **kwargs):
        language = (request.POST.get("language") or "en").lower()
        next_url = self.get_next_url(request)
        if language not in SUPPORTED_LANGUAGE_CODES:
            messages.warning(request, "That language is not available yet.")
            return redirect(next_url)

        response = redirect(next_url)
        self.apply_language_preference(request, response, language)
        return response


class DismissLanguageSuggestionView(View):
    cookie_max_age = 60 * 60 * 24 * 365

    def post(self, request, *args, **kwargs):
        next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("core:home")
        if not url_has_allowed_host_and_scheme(
            url=next_url,
            allowed_hosts={request.get_host()},
            require_https=request.is_secure(),
        ):
            next_url = reverse("core:home")
        next_url = remove_language_query_param(next_url)
        dismissed_language = detect_browser_language(request) or "en"
        response = redirect(next_url)
        response.set_cookie(
            LANGUAGE_PROMPT_DISMISSED_COOKIE,
            dismissed_language,
            max_age=self.cookie_max_age,
            samesite="Lax",
        )
        return response


def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /language/",
        "Disallow: /account/",
        "Disallow: /login/",
        "Disallow: /logout/",
        "Disallow: /signup/",
        "Disallow: /password-reset/",
        "Disallow: /saved/",
        "Disallow: /notifications/",
        "Disallow: /support/",
        "Disallow: /inquiries/",
        "Disallow: /company/",
        "Disallow: /stocklots/create/",
        "Disallow: /stocklots/mine/",
        "Disallow: /rfqs/create/",
        "Disallow: /rfqs/mine/",
        "Disallow: /rfqs/conversations/",
        "Disallow: /control/",
        "Disallow: /admin/",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


class SavedItemsView(LoginRequiredMixin, TemplateView):
    template_name = "core/saved.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["saved_listings"] = (
            Favorite.objects.select_related("stocklot", "stocklot__company", "stocklot__company__owner", "stocklot__category", "stocklot__category__parent")
            .filter(user=self.request.user, stocklot__status=Stocklot.Status.APPROVED, stocklot__is_active=True)
            .order_by("-created_at")
        )
        context["saved_rfqs"] = (
            RFQFavorite.objects.select_related("rfq", "rfq__buyer", "rfq__category", "rfq__category__parent")
            .filter(
                user=self.request.user,
                rfq__status=RFQ.Status.OPEN,
                rfq__moderation_status=RFQ.ModerationStatus.APPROVED,
            )
            .order_by("-created_at")
        )
        return context


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "core/notifications.html"
    context_object_name = "notifications"
    paginate_by = 20

    def get_queryset(self):
        qs = Notification.objects.filter(recipient=self.request.user).order_by("-created_at")
        if self.request.GET.get("filter") == "unread":
            qs = qs.filter(is_read=False)
        return qs


class NotificationMarkReadView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        notif = get_object_or_404(Notification, pk=kwargs["pk"], recipient=request.user)
        notif.is_read = True
        notif.save(update_fields=["is_read"])
        next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("core:notifications")
        messages.info(request, "Notification marked as read.")
        return redirect(next_url)


class NotificationMarkAllView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
        messages.info(request, "All notifications marked as read.")
        next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("core:notifications")
        return redirect(next_url)


class StaffRequiredMixin(UserPassesTestMixin, LoginRequiredMixin):
    def test_func(self):
        return self.request.user.is_staff


class AdminDashboardView(StaffRequiredMixin, TemplateView):
    template_name = "core/control.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Overview metrics
        from accounts.models import BuyerVerificationRequest, SellerVerificationRequest
        verified_any_q = models.Q(is_verified_user=True) | models.Q(
            buyer_verification_request__status=BuyerVerificationRequest.Status.VERIFIED
        ) | models.Q(seller_verification_request__status=SellerVerificationRequest.Status.APPROVED)
        ctx["metrics"] = {
            "users": User.objects.count(),
            "users_verified": User.objects.filter(verified_any_q).count(),
            "users_unverified": User.objects.exclude(verified_any_q).count(),
            "buyers": User.objects.filter(is_buyer=True).count(),
            "sellers": User.objects.filter(is_seller=True).count(),
            "companies": Company.objects.count(),
            "stocklots": Stocklot.objects.count(),
            "stocklots_approved": Stocklot.objects.filter(status=Stocklot.Status.APPROVED).count(),
            "stocklots_pending": Stocklot.objects.filter(status=Stocklot.Status.PENDING_REVIEW).count(),
            "rfqs": RFQ.objects.count(),
            "rfqs_open": RFQ.objects.filter(status=RFQ.Status.OPEN).count(),
            "inquiries": Inquiry.objects.count(),
            "inquiry_replies_pending": InquiryReply.objects.filter(
                moderation_status=InquiryReply.ModerationStatus.PENDING_REVIEW
            ).count(),
            "rfq_conversations": RFQConversation.objects.count(),
            "rfq_messages_pending": RFQMessage.objects.filter(
                moderation_status=RFQMessage.ModerationStatus.PENDING_REVIEW
            ).count(),
            "notifications": Notification.objects.count(),
            "deal_pending": DealTrigger.objects.filter(status=DealTrigger.Status.MUTUAL).count(),
        }
        ctx["latest_activity"] = Notification.objects.select_related("recipient", "actor").order_by("-created_at")[:20]
        ctx["latest_users"] = User.objects.order_by("-date_joined")[:10]
        ctx["latest_stocklots"] = Stocklot.objects.select_related("company").order_by("-created_at")[:10]
        ctx["latest_rfqs"] = RFQ.objects.select_related("buyer").order_by("-created_at")[:10]

        ctx["pending_deals"] = DealTrigger.objects.filter(status=DealTrigger.Status.MUTUAL).select_related(
            "inquiry", "rfq_conversation", "buyer", "seller_company"
        )[:50]
        ctx["pending_rfq_messages"] = RFQMessage.objects.filter(
            moderation_status=RFQMessage.ModerationStatus.PENDING_REVIEW
        ).select_related("conversation__rfq", "sender_user")[:50]
        ctx["pending_inquiry_replies"] = InquiryReply.objects.filter(
            moderation_status=InquiryReply.ModerationStatus.PENDING_REVIEW
        ).select_related("inquiry__stocklot", "sender_user")[:50]
        ctx["pending_stocklots"] = Stocklot.objects.filter(status=Stocklot.Status.PENDING_REVIEW).select_related(
            "company", "category"
        )[:50]
        ctx["hidden_companies"] = Company.objects.filter(identity_status=Company.IdentityStatus.HIDDEN)[:30]
        ctx["hidden_users"] = User.objects.filter(identity_status=User.IdentityStatus.HIDDEN)[:30]
        # Pending identity requests (deal history entries)
        ctx["identity_requests"] = (
            DealHistory.objects.filter(action="identity_request")
            .select_related("deal__buyer", "deal__seller_user", "deal__inquiry", "deal__rfq_conversation", "actor")
            .order_by("-created_at")[:50]
        )

        # Monitoring lists with filters
        listing_status = self.request.GET.get("listing_status")
        listings_qs = Stocklot.objects.select_related("company", "category")
        if listing_status:
            listings_qs = listings_qs.filter(status=listing_status)
        ctx["all_listings"] = listings_qs.order_by("-created_at")[:50]

        rfq_status = self.request.GET.get("rfq_status")
        rfq_qs = RFQ.objects.select_related("buyer")
        if rfq_status:
            rfq_qs = rfq_qs.filter(status=rfq_status)
        ctx["all_rfqs"] = rfq_qs.order_by("-created_at")[:50]

        inquiry_status = self.request.GET.get("inquiry_status")
        inquiry_qs = Inquiry.objects.select_related("buyer", "seller_company", "stocklot")
        if inquiry_status:
            inquiry_qs = inquiry_qs.filter(status=inquiry_status)
        ctx["all_inquiries"] = inquiry_qs.order_by("-created_at")[:50]

        convo_qs = RFQConversation.objects.select_related("rfq", "buyer", "seller_company")
        ctx["all_conversations"] = convo_qs.order_by("-created_at")[:50]

        # User search
        user_search = self.request.GET.get("user_search")
        users_qs = User.objects.all()
        if user_search:
            users_qs = users_qs.filter(email__icontains=user_search)
        ctx["users_manage"] = users_qs.select_related().order_by("-date_joined")[:50]

        # Company search
        company_search = self.request.GET.get("company_search")
        company_qs = Company.objects.select_related("owner")
        if company_search:
            company_qs = company_qs.filter(name__icontains=company_search)
        ctx["companies_manage"] = company_qs.order_by("name")[:50]

        # Visibility grants
        ctx["buyer_grants"] = BuyerVisibilityGrant.objects.select_related("buyer", "target_company").order_by("-created_at")[:50]
        ctx["company_grants"] = CompanyVisibilityGrant.objects.select_related("company", "target_buyer").order_by("-created_at")[:50]
        return ctx
        return ctx


class ModerateDealView(StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        deal = get_object_or_404(DealTrigger, pk=kwargs["pk"])
        decision = kwargs.get("decision")
        url = ""
        try:
            url = deal.inquiry.get_absolute_url()
        except Exception:
            try:
                url = deal.rfq_conversation and reverse("rfqs:conversation_detail", args=[deal.rfq_conversation.pk])
            except Exception:
                url = ""
        if decision == "approve":
            deal.status = DealTrigger.Status.APPROVED
            if deal.progress_status == DealTrigger.Progress.NOT_STARTED:
                deal.progress_status = DealTrigger.Progress.NOT_STARTED
            deal.save(update_fields=["status", "progress_status", "updated_at"])
            from core.models import DealHistory
            DealHistory.objects.create(deal=deal, actor=request.user, action="approved", note="Approved by admin")
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
            messages.success(request, "Deal approved.")
        elif decision == "reject":
            deal.status = DealTrigger.Status.REJECTED
            deal.save(update_fields=["status", "updated_at"])
            from core.models import DealHistory
            DealHistory.objects.create(deal=deal, actor=request.user, action="rejected", note="Rejected by admin")
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
            messages.info(request, "Deal rejected.")
        _broadcast_deal(deal)
        return redirect("core:control")


class ModerateRFQMessageView(StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        msg = get_object_or_404(RFQMessage, pk=kwargs["pk"])
        decision = kwargs.get("decision")
        if decision == "approve":
            msg.moderation_status = RFQMessage.ModerationStatus.APPROVED
            msg.save(update_fields=["moderation_status"])
            messages.success(request, "RFQ message approved.")
        elif decision == "reject":
            msg.moderation_status = RFQMessage.ModerationStatus.REJECTED
            msg.save(update_fields=["moderation_status"])
            create_notification(
                recipient=msg.sender_user,
                actor=request.user,
                notification_type=Notification.Type.DEAL_UPDATED,
                title="RFQ message rejected",
                body="Admin rejected your RFQ message.",
                url=reverse("rfqs:conversation_detail", args=[msg.conversation_id]),
            )
        return redirect("core:control")


class ModerateInquiryReplyView(StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        reply = get_object_or_404(InquiryReply, pk=kwargs["pk"])
        decision = kwargs.get("decision")
        if decision == "approve":
            reply.moderation_status = InquiryReply.ModerationStatus.APPROVED
            reply.save(update_fields=["moderation_status"])
            messages.success(request, "Inquiry reply approved.")
        elif decision == "reject":
            reply.moderation_status = InquiryReply.ModerationStatus.REJECTED
            reply.save(update_fields=["moderation_status"])
            create_notification(
                recipient=reply.sender_user,
                actor=request.user,
                notification_type=Notification.Type.DEAL_UPDATED,
                title="Inquiry reply rejected",
                body="Admin rejected your inquiry reply.",
                url=reply.inquiry.get_absolute_url(),
            )
        return redirect("core:control")


class ModerateStocklotView(StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        lot = get_object_or_404(Stocklot, pk=kwargs["pk"])
        decision = kwargs.get("decision")
        if decision == "approve":
            lot.status = Stocklot.Status.APPROVED
            lot.save(update_fields=["status"])
            messages.success(request, "Stocklot approved.")
        elif decision == "reject":
            lot.status = Stocklot.Status.REJECTED
            lot.save(update_fields=["status"])
            create_notification(
                recipient=lot.company.owner,
                actor=request.user,
                notification_type=Notification.Type.DEAL_UPDATED,
                title="Listing rejected",
                body=f"Listing {lot.title} was rejected by admin.",
                url=lot.get_absolute_url(),
            )
        return redirect("core:control")


class IdentityToggleView(StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        model = kwargs.get("model")
        obj_id = kwargs.get("pk")
        decision = kwargs.get("decision")
        if model == "company":
            obj = get_object_or_404(Company, pk=obj_id)
            if decision == "reveal":
                obj.identity_status = Company.IdentityStatus.REVEALED
            else:
                obj.identity_status = Company.IdentityStatus.HIDDEN
            obj.save(update_fields=["identity_status"])
        elif model == "user":
            obj = get_object_or_404(User, pk=obj_id)
            if decision == "reveal":
                obj.identity_status = obj.IdentityStatus.REVEALED
            else:
                obj.identity_status = obj.IdentityStatus.HIDDEN
            obj.save(update_fields=["identity_status"])
        messages.info(request, "Identity visibility updated.")
        return redirect("core:control")


class ToggleUserActiveView(StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs["pk"])
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        messages.info(request, f"User {user.email} active={user.is_active}.")
        return redirect("core:control")


class CreateVisibilityGrantView(StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        direction = kwargs.get("direction")
        target_user_id = request.POST.get("user_id")
        target_company_id = request.POST.get("company_id")
        if direction == "buyer_to_company":
            buyer = get_object_or_404(User, pk=target_user_id)
            company = get_object_or_404(Company, pk=target_company_id)
            BuyerVisibilityGrant.objects.get_or_create(
                buyer=buyer,
                target_company=company,
                defaults={
                    "scope": BuyerVisibilityGrant.Scope.SINGLE,
                    "status": BuyerVisibilityGrant.Status.APPROVED,
                    "granted_by": request.user,
                },
            )
            messages.success(request, "Grant created (buyer -> company).")
        elif direction == "company_to_buyer":
            company = get_object_or_404(Company, pk=target_company_id)
            buyer = get_object_or_404(User, pk=target_user_id)
            CompanyVisibilityGrant.objects.get_or_create(
                company=company,
                target_buyer=buyer,
                defaults={
                    "scope": CompanyVisibilityGrant.Scope.SINGLE,
                    "status": CompanyVisibilityGrant.Status.APPROVED,
                    "granted_by": request.user,
                },
            )
            messages.success(request, "Grant created (company -> buyer).")
        return redirect("core:control")


class RevokeVisibilityGrantView(StaffRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        grant_type = kwargs.get("grant_type")
        grant_id = kwargs.get("pk")
        if grant_type == "buyer":
            grant = get_object_or_404(BuyerVisibilityGrant, pk=grant_id)
        else:
            grant = get_object_or_404(CompanyVisibilityGrant, pk=grant_id)
        grant.status = grant.Status.REVOKED
        grant.save(update_fields=["status"])
        messages.info(request, "Grant revoked.")
        return redirect("core:control")


# ---------- CRUD style control pages (plain language, staff only) ----------


class PlainListMixin(StaffRequiredMixin):
    """Common helpers for control panel list views."""

    template_name = "core/control_list.html"
    context_object_name = "items"
    title = ""
    description = ""
    create_url = ""
    columns = ()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = self.title
        ctx["description"] = self.description
        ctx["create_url"] = self.create_url
        ctx["columns"] = self.columns
        return ctx


class PlainDetailMixin(StaffRequiredMixin):
    template_name = "core/control_detail.html"
    context_object_name = "item"
    title = ""
    fields = ()
    related_blocks = ()
    edit_url_name = ""
    delete_url_name = ""

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["title"] = self.title
        ctx["fields"] = self.fields
        ctx["related_blocks"] = self.related_blocks
        ctx["edit_url_name"] = self.edit_url_name
        ctx["delete_url_name"] = self.delete_url_name
        return ctx


# Users
class UserListView(PlainListMixin, ListView):
    model = User
    paginate_by = 50
    title = "People"
    description = "All users with buyer/seller role and identity status."
    create_url = reverse_lazy("core:control_user_create")
    columns = (
        ("Name / Email", "full_name"),
        ("Roles", "roles"),
        ("Verified", "is_verified_user"),
        ("Identity", "identity_status"),
        ("Active", "is_active"),
        ("Company", "company"),
    )

    def get_queryset(self):
        qs = User.objects.select_related("company").order_by("-date_joined")
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(models.Q(email__icontains=search) | models.Q(full_name__icontains=search))
        verification = self.request.GET.get("verification")
        from accounts.models import BuyerVerificationRequest, SellerVerificationRequest

        if verification == "verified_user":
            qs = qs.filter(is_verified_user=True)
        elif verification == "unverified":
            qs = qs.filter(
                models.Q(is_verified_user=False),
                models.Q(buyer_verification_request__status__isnull=True)
                | ~models.Q(buyer_verification_request__status=BuyerVerificationRequest.Status.VERIFIED),
                models.Q(seller_verification_request__status__isnull=True)
                | ~models.Q(seller_verification_request__status=SellerVerificationRequest.Status.APPROVED),
            )
        elif verification == "buyer_verified":
            qs = qs.filter(buyer_verification_request__status=BuyerVerificationRequest.Status.VERIFIED)
        elif verification == "seller_verified":
            qs = qs.filter(seller_verification_request__status=SellerVerificationRequest.Status.APPROVED)
        elif verification == "any_verified":
            qs = qs.filter(
                models.Q(is_verified_user=True)
                | models.Q(buyer_verification_request__status=BuyerVerificationRequest.Status.VERIFIED)
                | models.Q(seller_verification_request__status=SellerVerificationRequest.Status.APPROVED)
            )
        elif verification == "pending":
            qs = qs.filter(
                models.Q(buyer_verification_request__status=BuyerVerificationRequest.Status.PENDING)
                | models.Q(seller_verification_request__status=SellerVerificationRequest.Status.PENDING)
            )
        elif verification == "rejected":
            qs = qs.filter(
                models.Q(buyer_verification_request__status=BuyerVerificationRequest.Status.REJECTED)
                | models.Q(seller_verification_request__status=SellerVerificationRequest.Status.REJECTED)
            )
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["verification"] = self.request.GET.get("verification") or ""
        ctx["verification_filters"] = [
            ("", "All"),
            ("verified_user", "Verified users"),
            ("unverified", "Unverified users"),
            ("any_verified", "Any verified (global/buyer/seller)"),
            ("buyer_verified", "Buyer verified"),
            ("seller_verified", "Seller verified"),
            ("pending", "Pending verification"),
            ("rejected", "Rejected verification"),
        ]
        return ctx


class UserDetailView(PlainDetailMixin, DetailView):
    model = User
    title = "User profile"
    fields = (
        ("Name", "full_name"),
        ("Email", "email"),
        ("Verified user", "verified_user_label"),
        ("Verified at", "verified_user_at"),
        ("Verified by", "verified_user_by"),
        ("Verification note", "verified_user_note"),
        ("Buyer", "is_buyer"),
        ("Seller", "is_seller"),
        ("Active", "is_active"),
        ("Identity", "get_identity_status_display"),
        ("Company", "company"),
    )
    edit_url_name = "core:control_user_edit"
    delete_url_name = "core:control_user_delete"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self.object
        ctx["stats"] = {
            "listings": user.company.stocklots.count() if user.company else 0,
            "rfqs": getattr(user, "rfqs", []).count() if hasattr(user, "rfqs") else 0,
            "inquiries": user.sent_inquiries.count(),
            "conversations": user.rfq_conversations_as_buyer.count() + user.rfq_conversations_as_seller.count()
            if hasattr(user, "rfq_conversations_as_seller")
            else user.rfq_conversations_as_buyer.count(),
            "deals": user.deals_as_buyer.count() + user.deals_as_seller.count(),
        }
        return ctx


class UserCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = forms_admin.AdminUserForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_users")

    def form_valid(self, form):
        user = form.save(commit=False)
        if user.is_verified_user:
            user.verified_user_at = user.verified_user_at or timezone.now()
            user.verified_user_by = user.verified_user_by or self.request.user
        else:
            user.verified_user_at = None
            user.verified_user_by = None
            user.verified_user_note = ""
        user.save()
        form.save_m2m()
        messages.success(self.request, "User created.")
        return redirect(self.success_url)


class UserUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = forms_admin.AdminUserForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_users")

    def form_valid(self, form):
        user = form.save(commit=False)
        if user.is_verified_user:
            user.verified_user_at = user.verified_user_at or timezone.now()
            user.verified_user_by = user.verified_user_by or self.request.user
        else:
            user.verified_user_at = None
            user.verified_user_by = None
            user.verified_user_note = ""
        user.save()
        form.save_m2m()
        messages.success(self.request, "User updated.")
        return redirect(self.success_url)


class UserVerifyToggleView(StaffRequiredMixin, View):
    """Allow staff to mark or unmark a user as admin-verified."""

    def post(self, request, *args, **kwargs):
        user = get_object_or_404(User, pk=kwargs["pk"])
        action = kwargs.get("action")
        note = request.POST.get("note", "").strip()
        if action == "verify":
            user.is_verified_user = True
            user.verified_user_at = timezone.now()
            user.verified_user_by = request.user
            if note:
                user.verified_user_note = note
            user.save(update_fields=["is_verified_user", "verified_user_at", "verified_user_by", "verified_user_note"])
            messages.success(request, "User marked as verified.")
        elif action == "unverify":
            user.is_verified_user = False
            user.verified_user_at = None
            user.verified_user_by = None
            user.verified_user_note = ""
            user.save(update_fields=["is_verified_user", "verified_user_at", "verified_user_by", "verified_user_note"])
            messages.info(request, "User verification removed.")
        else:
            messages.error(request, "Invalid verification action.")
        next_url = request.META.get("HTTP_REFERER") or reverse("core:control_user_detail", args=[user.pk])
        return redirect(next_url)


class UserDeleteView(StaffRequiredMixin, DeleteView):
    model = User
    template_name = "core/control_confirm_delete.html"
    success_url = reverse_lazy("core:control_users")

    def delete(self, request, *args, **kwargs):
        messages.warning(request, "User deleted.")
        return super().delete(request, *args, **kwargs)


# Companies
class CompanyListView(PlainListMixin, ListView):
    model = Company
    paginate_by = 50
    title = "Companies"
    description = "Business profiles and their visibility."
    create_url = reverse_lazy("core:control_company_create")
    columns = (
        ("Company", "name"),
        ("Owner", "owner"),
        ("Identity", "identity_status"),
        ("Country", "country"),
    )

    def get_queryset(self):
        qs = Company.objects.select_related("owner").order_by("name")
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(name__icontains=search)
        return qs


class CompanyDetailView(PlainDetailMixin, DetailView):
    model = Company
    title = "Company profile"
    fields = (
        ("Name", "name"),
        ("Owner", "owner"),
        ("Identity", "get_identity_status_display"),
        ("Country", "country"),
        ("City", "city"),
        ("Phone", "phone"),
        ("Email", "email"),
        ("Website", "website"),
    )
    edit_url_name = "core:control_company_edit"
    delete_url_name = "core:control_company_delete"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        company = self.object
        ctx["stats"] = {
            "listings": company.stocklots.count(),
            "inquiries": company.received_inquiries.count(),
            "conversations": company.rfqconversation_set.count(),
            "deals": company.deals.count(),
        }
        return ctx


class CompanyCreateView(StaffRequiredMixin, CreateView):
    model = Company
    form_class = forms_admin.AdminCompanyForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_companies")

    def form_valid(self, form):
        messages.success(self.request, "Company created.")
        return super().form_valid(form)


class CompanyUpdateView(StaffRequiredMixin, UpdateView):
    model = Company
    form_class = forms_admin.AdminCompanyForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_companies")

    def form_valid(self, form):
        messages.success(self.request, "Company updated.")
        return super().form_valid(form)


class CompanyDeleteView(StaffRequiredMixin, DeleteView):
    model = Company
    template_name = "core/control_confirm_delete.html"
    success_url = reverse_lazy("core:control_companies")

    def delete(self, request, *args, **kwargs):
        messages.warning(request, "Company deleted.")
        return super().delete(request, *args, **kwargs)


# Deals
class DealListView(PlainListMixin, ListView):
    model = DealTrigger
    paginate_by = 50
    title = "Deals & Agreements"
    description = "Track all deal triggers with status and parties."
    create_url = reverse_lazy("core:control_deal_create")
    columns = (
        ("ID", "id"),
        ("Type", "deal_type"),
        ("Status", "status"),
        ("Progress", "progress_status"),
        ("Buyer", "buyer"),
        ("Seller", "seller_user"),
        ("Company", "seller_company"),
        ("Inquiry", "inquiry"),
        ("RFQ conversation", "rfq_conversation"),
        ("Updated", "updated_at"),
    )

    def get_queryset(self):
        qs = DealTrigger.objects.select_related(
            "buyer", "seller_user", "seller_company", "inquiry", "rfq_conversation"
        ).order_by("-updated_at")
        status = self.request.GET.get("status")
        progress = self.request.GET.get("progress")
        if status:
            qs = qs.filter(status=status)
        if progress:
            qs = qs.filter(progress_status=progress)
        return qs


class DealDetailView(PlainDetailMixin, DetailView):
    model = DealTrigger
    template_name = "core/deal_detail.html"
    title = "Deal details"
    fields = (
        ("Deal type", "deal_type"),
        ("Status", "status"),
        ("Progress", "progress_status"),
        ("Buyer accepted", "buyer_accepted"),
        ("Seller accepted", "seller_accepted"),
        ("Buyer", "buyer"),
        ("Seller user", "seller_user"),
        ("Seller company", "seller_company"),
        ("Inquiry", "inquiry"),
        ("RFQ conversation", "rfq_conversation"),
        ("Created", "created_at"),
        ("Updated", "updated_at"),
    )
    edit_url_name = "core:control_deal_edit"
    delete_url_name = "core:control_deal_delete"


class DealCreateView(StaffRequiredMixin, CreateView):
    model = DealTrigger
    form_class = forms_admin.AdminDealForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_deals")

    def form_valid(self, form):
        messages.success(self.request, "Deal created.")
        return super().form_valid(form)


class DealUpdateView(StaffRequiredMixin, UpdateView):
    model = DealTrigger
    form_class = forms_admin.AdminDealForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_deals")

    def form_valid(self, form):
        messages.success(self.request, "Deal updated.")
        return super().form_valid(form)


class DealDeleteView(StaffRequiredMixin, DeleteView):
    model = DealTrigger
    template_name = "core/control_confirm_delete.html"
    success_url = reverse_lazy("core:control_deals")

    def delete(self, request, *args, **kwargs):
        messages.warning(request, "Deal removed.")
        return super().delete(request, *args, **kwargs)


class DealProgressView(StaffRequiredMixin, View):
    """Update post-approval progress: in_progress -> ready -> completed or cancel."""

    def post(self, request, *args, **kwargs):
        deal = get_object_or_404(DealTrigger, pk=kwargs["pk"])
        action = kwargs.get("action")
        note = ""
        if action == "start":
            deal.progress_status = DealTrigger.Progress.IN_PROGRESS
            note = "Marked in progress"
            title = "Deal in progress"
        elif action == "ready":
            if deal.progress_status in [DealTrigger.Progress.IN_PROGRESS, DealTrigger.Progress.NOT_STARTED]:
                deal.progress_status = DealTrigger.Progress.READY
                note = "Marked ready"
                title = "Deal ready"
            else:
                messages.error(request, "Set to in progress first.")
                return redirect(reverse("core:control_deal_detail", args=[deal.pk]))
        elif action == "complete":
            if deal.progress_status in [DealTrigger.Progress.READY, DealTrigger.Progress.IN_PROGRESS]:
                deal.progress_status = DealTrigger.Progress.COMPLETED
                note = "Marked completed"
                title = "Deal completed"
            else:
                messages.error(request, "Set to ready before completing.")
                return redirect(reverse("core:control_deal_detail", args=[deal.pk]))
        elif action == "cancel":
            deal.status = DealTrigger.Status.CANCELLED
            deal.progress_status = DealTrigger.Progress.NOT_STARTED
            note = "Deal cancelled"
            title = "Deal cancelled"
        else:
            messages.error(request, "Unknown action.")
            return redirect(reverse("core:control_deal_detail", args=[deal.pk]))

        deal.save(update_fields=["status", "progress_status", "updated_at"])
        # history log
        from core.models import DealHistory

        DealHistory.objects.create(deal=deal, actor=request.user, action=action, note=note)
        # notify parties
        from core.utils.notifications import create_notification

        url = ""
        try:
            url = deal.inquiry.get_absolute_url()
        except Exception:
            try:
                url = reverse("rfqs:conversation_detail", args=[deal.rfq_conversation_id])
            except Exception:
                url = ""
        for recipient in [deal.buyer, deal.seller_user]:
            if recipient:
                create_notification(
                    recipient=recipient,
                    actor=request.user,
                    notification_type=Notification.Type.DEAL_UPDATED,
                    title=title,
                    body=note,
                    url=url,
                )
        messages.success(request, note)
        _broadcast_deal(deal)
        return redirect(reverse("core:control_deal_detail", args=[deal.pk]))


# Stocklots
class StocklotListView(PlainListMixin, ListView):
    model = Stocklot
    paginate_by = 50
    title = "Listings"
    description = "All stocklots with quick status review."
    create_url = reverse_lazy("core:control_stocklot_create")
    columns = (
        ("Title", "title"),
        ("Company", "company"),
        ("Status", "status"),
        ("Verified", "is_admin_verified"),
        ("Price", "price"),
        ("Country", "location_country"),
        ("Updated", "updated_at"),
    )

    def get_queryset(self):
        qs = Stocklot.objects.select_related("company", "category").order_by("-updated_at")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        return qs


class StocklotDetailView(PlainDetailMixin, DetailView):
    model = Stocklot
    template_name = "core/stocklot_control_detail.html"
    title = "Listing detail"
    fields = (
        ("Title", "title"),
        ("Company", "company"),
        ("Status", "status"),
        ("Verified", "is_admin_verified"),
        ("Quantity", "quantity"),
        ("Unit", "unit_type"),
        ("Price", "price"),
        ("Country", "location_country"),
        ("City", "location_city"),
        ("Updated", "updated_at"),
    )
    edit_url_name = "core:control_stocklot_edit"
    delete_url_name = "core:control_stocklot_delete"


class StocklotCreateView(StaffRequiredMixin, CreateView):
    model = Stocklot
    form_class = forms_admin.AdminStocklotForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_stocklots")

    def form_valid(self, form):
        messages.success(self.request, "Listing created.")
        return super().form_valid(form)


class StocklotUpdateView(StaffRequiredMixin, UpdateView):
    model = Stocklot
    form_class = forms_admin.AdminStocklotForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_stocklots")

    def form_valid(self, form):
        messages.success(self.request, "Listing updated.")
        return super().form_valid(form)


class StocklotDeleteView(StaffRequiredMixin, DeleteView):
    model = Stocklot
    template_name = "core/control_confirm_delete.html"
    success_url = reverse_lazy("core:control_stocklots")

    def delete(self, request, *args, **kwargs):
        messages.warning(request, "Listing deleted.")
        return super().delete(request, *args, **kwargs)


# RFQs
class RFQListView(PlainListMixin, ListView):
    model = RFQ
    paginate_by = 50
    title = "RFQs"
    description = "Open buyer requests and their status."
    create_url = reverse_lazy("core:control_rfq_create")
    template_name = "core/rfq_control_list.html"
    columns = (
        ("Title", "title"),
        ("Buyer", "buyer"),
        ("Status", "status"),
        ("Quantity", "quantity"),
        ("Country", "location_country"),
        ("Updated", "updated_at"),
    )

    def get_queryset(self):
        qs = RFQ.objects.select_related("buyer").order_by("-updated_at")
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        mod = self.request.GET.get("moderation_status")
        if mod:
            qs = qs.filter(moderation_status=mod)
        if self.request.GET.get("has_conversations") == "1":
            qs = qs.filter(conversations__isnull=False).distinct()
        if self.request.GET.get("has_pending_messages") == "1":
            qs = qs.filter(conversations__messages__moderation_status=RFQMessage.ModerationStatus.PENDING_REVIEW).distinct()
        if self.request.GET.get("has_deal") == "1":
            qs = qs.filter(conversations__deal_trigger__isnull=False).distinct()
        return qs


class RFQDetailView(PlainDetailMixin, DetailView):
    model = RFQ
    template_name = "core/rfq_control_detail.html"
    title = "RFQ detail"
    edit_url_name = "core:control_rfq_edit"
    delete_url_name = "core:control_rfq_delete"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        rfq = self.object
        conversations = rfq.conversations.select_related("buyer", "seller_company", "seller_user").prefetch_related(
            "messages", "deal_trigger"
        )
        convo_data = []
        for c in conversations:
            messages = list(c.messages.all())
            pending = [m for m in messages if m.moderation_status == RFQMessage.ModerationStatus.PENDING_REVIEW]
            convo_data.append(
                {
                    "conversation": c,
                    "messages_count": len(messages),
                    "pending_count": len(pending),
                    "deal": getattr(c, "deal_trigger", None),
                }
            )
        ctx["conversations"] = convo_data
        ctx["messages_count"] = RFQMessage.objects.filter(conversation__rfq=rfq).count()
        ctx["messages_pending"] = RFQMessage.objects.filter(
            conversation__rfq=rfq, moderation_status=RFQMessage.ModerationStatus.PENDING_REVIEW
        ).count()
        ctx["deal_count"] = DealTrigger.objects.filter(rfq_conversation__rfq=rfq).count()
        return ctx


class RFQCreateView(StaffRequiredMixin, CreateView):
    model = RFQ
    form_class = forms_admin.AdminRFQForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_rfqs")

    def form_valid(self, form):
        messages.success(self.request, "RFQ created.")
        return super().form_valid(form)


class RFQUpdateView(StaffRequiredMixin, UpdateView):
    model = RFQ
    form_class = forms_admin.AdminRFQForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_rfqs")

    def form_valid(self, form):
        messages.success(self.request, "RFQ updated.")
        return super().form_valid(form)


class RFQDeleteView(StaffRequiredMixin, DeleteView):
    model = RFQ
    template_name = "core/control_confirm_delete.html"
    success_url = reverse_lazy("core:control_rfqs")

    def delete(self, request, *args, **kwargs):
        messages.warning(request, "RFQ deleted.")
        return super().delete(request, *args, **kwargs)


class RFQStatusView(StaffRequiredMixin, View):
    """Approve/Reject or Close/Reopen RFQ."""

    def post(self, request, *args, **kwargs):
        rfq = get_object_or_404(RFQ, pk=kwargs["pk"])
        action = kwargs.get("action")
        if action == "approve":
            rfq.moderation_status = RFQ.ModerationStatus.APPROVED
            note = "RFQ approved"
        elif action == "reject":
            rfq.moderation_status = RFQ.ModerationStatus.REJECTED
            note = "RFQ rejected"
        elif action == "close":
            rfq.status = RFQ.Status.CLOSED
            note = "RFQ closed"
        elif action == "open":
            rfq.status = RFQ.Status.OPEN
            note = "RFQ reopened"
        else:
            messages.error(request, "Unknown action.")
            return redirect("core:control_rfqs")
        rfq.save(update_fields=["status", "moderation_status", "updated_at"])
        # Notify owner on approval/rejection
        from core.models import Notification
        from core.utils.notifications import create_notification

        if action in ["approve", "reject"]:
            notif_type = Notification.Type.RFQ_APPROVED if action == "approve" else Notification.Type.SYSTEM
            create_notification(
                recipient=rfq.buyer,
                actor=request.user,
                notification_type=notif_type,
                title=note,
                body=f"Your RFQ '{rfq.title}' was {note.lower()}.",
                url=rfq.get_absolute_url(),
            )
        messages.success(request, note)
        return redirect("core:control_rfq_detail", rfq.pk)


# Inquiries (readable moderation / CRUD)
class InquiryListView(PlainListMixin, ListView):
    model = Inquiry
    paginate_by = 50
    title = "Inquiries"
    description = "Buyer questions to sellers."
    create_url = reverse_lazy("core:control_inquiry_create")
    columns = (
        ("Subject", "subject"),
        ("Stocklot", "stocklot"),
        ("Buyer", "buyer"),
        ("Seller company", "seller_company"),
        ("Status", "status"),
        ("Updated", "updated_at"),
    )

    def get_queryset(self):
        qs = Inquiry.objects.select_related("buyer", "seller_company", "stocklot").order_by("-updated_at")
        return qs


class InquiryDetailView(PlainDetailMixin, DetailView):
    model = Inquiry
    title = "Inquiry detail"
    fields = (
        ("Subject", "subject"),
        ("Stocklot", "stocklot"),
        ("Buyer", "buyer"),
        ("Seller company", "seller_company"),
        ("Status", "status"),
        ("Message", "message"),
        ("Updated", "updated_at"),
    )
    edit_url_name = "core:control_inquiry_edit"
    delete_url_name = "core:control_inquiry_delete"


class InquiryCreateView(StaffRequiredMixin, CreateView):
    model = Inquiry
    form_class = forms_admin.AdminInquiryForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_inquiries")

    def form_valid(self, form):
        messages.success(self.request, "Inquiry created.")
        return super().form_valid(form)


class InquiryUpdateView(StaffRequiredMixin, UpdateView):
    model = Inquiry
    form_class = forms_admin.AdminInquiryForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_inquiries")

    def form_valid(self, form):
        messages.success(self.request, "Inquiry updated.")
        return super().form_valid(form)


class InquiryDeleteView(StaffRequiredMixin, DeleteView):
    model = Inquiry
    template_name = "core/control_confirm_delete.html"
    success_url = reverse_lazy("core:control_inquiries")

    def delete(self, request, *args, **kwargs):
        messages.warning(request, "Inquiry deleted.")
        return super().delete(request, *args, **kwargs)


# Inquiry replies and RFQ messages: simple read/update for moderation/cleanup
class InquiryReplyListView(PlainListMixin, ListView):
    model = InquiryReply
    paginate_by = 50
    title = "Inquiry replies"
    description = "Messages inside inquiries."
    create_url = None
    columns = (
        ("Inquiry", "inquiry"),
        ("Sender", "sender_user"),
        ("Status", "moderation_status"),
        ("When", "created_at"),
    )

    def get_queryset(self):
        return InquiryReply.objects.select_related("inquiry", "sender_user").order_by("-created_at")


class InquiryReplyDetailView(StaffRequiredMixin, DetailView):
    model = InquiryReply
    template_name = "core/inquiry_reply_detail.html"
    context_object_name = "reply"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        reply = self.object
        inquiry = reply.inquiry
        ctx["inquiry"] = inquiry
        ctx["thread"] = inquiry.replies.select_related("sender_user", "sender_company").order_by("created_at")
        ctx["deal"] = getattr(inquiry, "deal_trigger", None)
        timeline = [
            ("Inquiry created", inquiry.created_at),
            ("Reply submitted", reply.created_at),
        ]
        if ctx["deal"]:
            deal = ctx["deal"]
            timeline.append((f"Deal status: {deal.get_status_display()}", deal.updated_at))
            timeline.append((f"Progress: {deal.get_progress_status_display()}", deal.updated_at))
        ctx["timeline"] = timeline
        return ctx


class InquiryReplyUpdateView(StaffRequiredMixin, UpdateView):
    model = InquiryReply
    form_class = forms_admin.AdminInquiryReplyForm
    template_name = "core/inquiry_reply_form.html"
    success_url = reverse_lazy("core:control_inquiry_replies_list")

    def form_valid(self, form):
        messages.success(self.request, "Inquiry reply updated.")
        return super().form_valid(form)


class InquiryReplyDeleteView(StaffRequiredMixin, DeleteView):
    model = InquiryReply
    template_name = "core/control_confirm_delete.html"
    success_url = reverse_lazy("core:control_inquiry_replies_list")

    def delete(self, request, *args, **kwargs):
        messages.warning(request, "Inquiry reply deleted.")
        return super().delete(request, *args, **kwargs)


class RFQMessageListView(PlainListMixin, ListView):
    model = RFQMessage
    paginate_by = 50
    title = "RFQ messages"
    description = "Replies inside RFQ conversations."
    create_url = None
    columns = (
        ("Conversation", "conversation"),
        ("Sender", "sender_user"),
        ("Status", "moderation_status"),
        ("When", "created_at"),
    )

    def get_queryset(self):
        return RFQMessage.objects.select_related("conversation", "sender_user").order_by("-created_at")


class RFQMessageDetailView(StaffRequiredMixin, DetailView):
    model = RFQMessage
    template_name = "core/rfqmessage_detail.html"
    context_object_name = "message"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        msg = self.object
        convo = msg.conversation
        rfq = convo.rfq
        ctx["conversation"] = convo
        ctx["rfq"] = rfq
        ctx["messages"] = convo.messages.select_related("sender_user", "sender_company").order_by("created_at")
        ctx["deal"] = getattr(convo, "deal_trigger", None)
        timeline = [
            ("RFQ created", rfq.created_at),
            ("Conversation started", convo.created_at),
            ("Message submitted", msg.created_at),
        ]
        if ctx["deal"]:
            deal = ctx["deal"]
            timeline.append((f"Deal status: {deal.get_status_display()}", deal.updated_at))
            timeline.append((f"Progress: {deal.get_progress_status_display()}", deal.updated_at))
        ctx["timeline"] = timeline
        return ctx


class RFQMessageUpdateView(StaffRequiredMixin, UpdateView):
    model = RFQMessage
    form_class = forms_admin.AdminRFQMessageForm
    template_name = "core/rfqmessage_form.html"
    success_url = reverse_lazy("core:control_rfq_messages_list")

    def form_valid(self, form):
        messages.success(self.request, "RFQ message updated.")
        return super().form_valid(form)


class RFQMessageDeleteView(StaffRequiredMixin, DeleteView):
    model = RFQMessage
    template_name = "core/control_confirm_delete.html"
    success_url = reverse_lazy("core:control_rfq_messages_list")

    def delete(self, request, *args, **kwargs):
        messages.warning(request, "RFQ message deleted.")
        return super().delete(request, *args, **kwargs)


# ------------------- Deal live status API -------------------


def _deal_state_dict(deal, viewer):
    """Serialize deal state for polling and live block."""

    def decision(accepted, rejected):
        if accepted:
            return "accepted"
        if rejected:
            return "rejected"
        return "pending"

    buyer_dec = decision(deal.buyer_accepted, deal.buyer_rejected)
    seller_dec = decision(deal.seller_accepted, deal.seller_rejected)
    admin_dec = (
        "approved"
        if deal.status == DealTrigger.Status.APPROVED
        else "rejected"
        if deal.status == DealTrigger.Status.REJECTED
        else "pending"
    )

    if deal.status == DealTrigger.Status.PENDING:
        overall = "Waiting for both sides"
    elif deal.status == DealTrigger.Status.MUTUAL:
        overall = "Both sides accepted – waiting for admin"
    elif deal.status == DealTrigger.Status.APPROVED:
        overall = "Deal approved"
    elif deal.status == DealTrigger.Status.REJECTED:
        overall = "Deal rejected"
    elif deal.status == DealTrigger.Status.CANCELLED:
        overall = "Deal cancelled"
    else:
        overall = deal.get_status_display()

    next_action = ""
    if deal.status == DealTrigger.Status.PENDING:
        if not deal.buyer_accepted and not deal.buyer_rejected:
            next_action = "Buyer must accept or reject"
        elif not deal.seller_accepted and not deal.seller_rejected:
            next_action = "Seller must accept or reject"
        else:
            next_action = "Waiting for the other side"
    elif deal.status == DealTrigger.Status.MUTUAL:
        next_action = "Admin approval required"
    elif deal.status == DealTrigger.Status.APPROVED:
        if deal.progress_status == DealTrigger.Progress.NOT_STARTED:
            next_action = "Move to in progress"
        elif deal.progress_status == DealTrigger.Progress.IN_PROGRESS:
            next_action = "Work in progress"
        elif deal.progress_status == DealTrigger.Progress.READY:
            next_action = "Mark completed when done"
        elif deal.progress_status == DealTrigger.Progress.COMPLETED:
            next_action = "Deal completed"
    elif deal.status == DealTrigger.Status.REJECTED:
        next_action = "Deal stopped (can be restarted)"
    elif deal.status == DealTrigger.Status.CANCELLED:
        next_action = "Deal cancelled (can be restarted)"

    can_accept = False
    can_reject = False
    can_cancel = False
    # Allow restarting even after cancelled/rejected; block only if fully approved
    if viewer == deal.buyer and not deal.buyer_accepted and deal.status != DealTrigger.Status.APPROVED:
        can_accept = True
        can_reject = True
    if viewer == deal.seller_user and not deal.seller_accepted and deal.status != DealTrigger.Status.APPROVED:
        can_accept = True
        can_reject = True
    if viewer in [deal.buyer, deal.seller_user] or getattr(viewer, "is_staff", False):
        can_cancel = deal.status not in [DealTrigger.Status.APPROVED, DealTrigger.Status.REJECTED]

    history = []
    for h in deal.history.all()[:6]:
        actor = h.actor
        if actor is None:
            actor_label = "System"
        elif getattr(actor, "is_staff", False):
            actor_label = "Admin"
        else:
            if actor == deal.buyer:
                actor_label = f"Buyer ID #{actor.id}"
            elif actor == deal.seller_user:
                actor_label = f"Seller ID #{actor.id}"
            else:
                actor_label = f"User #{actor.id}"
        history.append(
            {
                "text": f"{actor_label}: {h.action} {h.note}".strip(),
                "ts": h.created_at.strftime("%Y-%m-%d %H:%M"),
            }
        )

    latest_event = history[0]["text"] if history else ""

    # Identity state per viewer
    buyer_status = _identity_status(deal, "buyer")
    seller_status = _identity_status(deal, "seller")
    buyer_real = deal.buyer.full_name or deal.buyer.email
    seller_real = deal.seller_company.name
    buyer_masked = f"Buyer ID #{deal.buyer_id}"
    seller_masked = f"Seller ID #{deal.seller_user_id}"
    is_buyer = viewer == deal.buyer
    is_seller = viewer == deal.seller_user
    staff = getattr(viewer, "is_staff", False)
    if is_buyer or staff:
        buyer_label = buyer_real
    elif buyer_status == "revealed":
        buyer_label = buyer_real
    else:
        buyer_label = buyer_masked

    if is_seller or staff:
        seller_label = seller_real
    elif seller_status == "revealed":
        seller_label = seller_real
    else:
        seller_label = seller_masked

    from core.utils.verification import is_verified
    can_reveal_buyer = is_buyer and buyer_status == "hidden" and is_verified(viewer, "buyer")
    can_reveal_seller = is_seller and seller_status == "hidden" and is_verified(viewer, "seller")
    # Allow requesting counterparty identity until it is actually revealed (pending requests stay visible)
    can_request_buyer = is_seller and buyer_status != "revealed" and is_verified(viewer, "seller")
    can_request_seller = is_buyer and seller_status != "revealed" and is_verified(viewer, "buyer")

    return {
        "overall_status": overall,
        "status": deal.status,
        "status_display": deal.get_status_display(),
        "progress": deal.get_progress_status_display(),
        "buyer_decision": buyer_dec,
        "seller_decision": seller_dec,
        "admin_decision": admin_dec,
        "next_action": next_action,
        "can_accept": can_accept,
        "can_reject": can_reject,
        "can_cancel": can_cancel,
        "buyer_identity_status": buyer_status,
        "seller_identity_status": seller_status,
        "buyer_label": buyer_label,
        "seller_label": seller_label,
        "can_reveal_buyer": can_reveal_buyer,
        "can_reveal_seller": can_reveal_seller,
        "can_request_buyer": can_request_buyer,
        "can_request_seller": can_request_seller,
        "latest_event": latest_event,
        "updated_at": deal.updated_at.isoformat(),
        "history": history,
    }


class DealStatusView(LoginRequiredMixin, View):
    """JSON status for polling; only participants or staff."""

    def get(self, request, *args, **kwargs):
        deal = get_object_or_404(DealTrigger, pk=kwargs["pk"])
        if not (request.user.is_staff or request.user in [deal.buyer, deal.seller_user]):
            return JsonResponse({"error": "forbidden"}, status=403)
        return JsonResponse(_deal_state_dict(deal, request.user))


class DealIdentityRequestView(LoginRequiredMixin, View):
    """Participant requests to reveal or hide counterparty identity; admin approves manually."""

    def post(self, request, *args, **kwargs):
        deal = get_object_or_404(DealTrigger, pk=kwargs["pk"])
        action = kwargs.get("action")  # 'reveal', 'hide', 'approve', 'reject'
        target = kwargs.get("target")  # 'buyer' or 'seller'
        if not (request.user.is_staff or request.user in [deal.buyer, deal.seller_user]):
            messages.error(request, "Not allowed.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        if target not in ("buyer", "seller") or action not in ("reveal", "hide", "approve", "reject"):
            messages.error(request, "Invalid request.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        url = ""
        try:
            url = deal.inquiry.get_absolute_url()
        except Exception:
            try:
                url = reverse("rfqs:conversation_detail", args=[deal.rfq_conversation_id])
            except Exception:
                url = ""

        # Participant request
        if action in ("reveal", "hide") and not request.user.is_staff:
            role = "buyer" if request.user == deal.buyer else "seller"
            ok, msg = enforce_verified(request, role=role)
            if not ok:
                messages.error(request, msg)
                return redirect(request.META.get("HTTP_REFERER", "/"))
            role = "Buyer" if request.user == deal.buyer else "Seller"
            note = f"{role} requested to {action} {target} identity"
            DealHistory.objects.create(deal=deal, actor=request.user, action="identity_request", note=note)
            for admin in User.objects.filter(is_staff=True):
                create_notification(
                    recipient=admin,
                    actor=request.user,
                    notification_type=Notification.Type.IDENTITY_REVEALED,
                    title="Identity request",
                    body=note,
                    url=url,
                )
            _broadcast_deal(deal)
            messages.info(request, "Request sent to admin for approval.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        # Admin approval/rejection
        if request.user.is_staff and action in ("approve", "reject"):
            if target == "buyer":
                deal.buyer_identity_revealed = action == "approve"
            else:
                deal.seller_identity_revealed = action == "approve"
            deal.save(update_fields=["buyer_identity_revealed", "seller_identity_revealed", "updated_at"])
            note = f"Admin {action}d identity for {target}"
            DealHistory.objects.create(deal=deal, actor=request.user, action="identity_decision", note=note)
            for recipient in [deal.buyer, deal.seller_user]:
                if recipient:
                    create_notification(
                        recipient=recipient,
                        actor=request.user,
                        notification_type=Notification.Type.IDENTITY_REVEALED,
                        title="Identity decision",
                        body=note,
                        url=url,
                    )
            _broadcast_deal(deal)
            messages.success(request, f"Identity {action}d.")
            return redirect(request.META.get("HTTP_REFERER", "/"))

        messages.error(request, "Invalid identity action.")
        return redirect(request.META.get("HTTP_REFERER", "/"))
