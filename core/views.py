from django.contrib import messages
from django.db import models
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, ListView, View, DetailView, CreateView, UpdateView, DeleteView

from stocklots.models import Stocklot
from core.models import Notification, DealTrigger
from rfqs.models import RFQMessage, RFQ, RFQConversation
from inquiries.models import InquiryReply, Inquiry
from companies.models import Company
from accounts.models import User
from core.utils.notifications import create_notification
from core.models import BuyerVisibilityGrant, CompanyVisibilityGrant
from core import forms_admin


class HomeView(TemplateView):
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["homepage_stocklots"] = (
            Stocklot.objects.select_related("company", "category", "category__parent")
            .filter(status=Stocklot.Status.APPROVED, is_active=True)
            .order_by("-created_at")[:6]
        )
        return context


class AboutView(TemplateView):
    template_name = "core/about.html"


class ContactView(TemplateView):
    template_name = "core/contact.html"


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
        ctx["metrics"] = {
            "users": User.objects.count(),
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
        ("Identity", "identity_status"),
        ("Active", "is_active"),
        ("Company", "company"),
    )

    def get_queryset(self):
        qs = User.objects.select_related("company").order_by("-date_joined")
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(models.Q(email__icontains=search) | models.Q(full_name__icontains=search))
        return qs


class UserDetailView(PlainDetailMixin, DetailView):
    model = User
    title = "User profile"
    fields = (
        ("Name", "full_name"),
        ("Email", "email"),
        ("Buyer", "is_buyer"),
        ("Seller", "is_seller"),
        ("Active", "is_active"),
        ("Identity", "get_identity_status_display"),
        ("Company", "company"),
    )
    edit_url_name = "core:control_user_edit"
    delete_url_name = "core:control_user_delete"


class UserCreateView(StaffRequiredMixin, CreateView):
    model = User
    form_class = forms_admin.AdminUserForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_users")

    def form_valid(self, form):
        messages.success(self.request, "User created.")
        return super().form_valid(form)


class UserUpdateView(StaffRequiredMixin, UpdateView):
    model = User
    form_class = forms_admin.AdminUserForm
    template_name = "core/control_form.html"
    success_url = reverse_lazy("core:control_users")

    def form_valid(self, form):
        messages.success(self.request, "User updated.")
        return super().form_valid(form)


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
        return qs


class RFQDetailView(PlainDetailMixin, DetailView):
    model = RFQ
    title = "RFQ detail"
    fields = (
        ("Title", "title"),
        ("Buyer", "buyer"),
        ("Status", "status"),
        ("Quantity", "quantity"),
        ("Unit", "unit_type"),
        ("Target price", "target_price"),
        ("Currency", "currency"),
        ("Country", "location_country"),
        ("City", "location_city"),
        ("Updated", "updated_at"),
    )
    edit_url_name = "core:control_rfq_edit"
    delete_url_name = "core:control_rfq_delete"


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
