from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, View

from companies.models import Company
from stocklots.models import Stocklot

from core.utils.deals import accept_deal, cancel_deal, get_or_create_for_inquiry
from .forms import InquiryForm
from .forms_reply import InquiryReplyForm
from .models import Inquiry, InquiryReply
from core.models import DealTrigger


class InquiryCreateView(LoginRequiredMixin, CreateView):
    model = Inquiry
    form_class = InquiryForm
    template_name = "inquiries/inquiry_form.html"

    def dispatch(self, request, *args, **kwargs):
        self.stocklot = get_object_or_404(
            Stocklot.objects.select_related("company"),
            slug=kwargs.get("stocklot_slug"),
        )
        if self.stocklot.company.owner_id == request.user.id:
            messages.info(request, "You cannot send an inquiry to your own listing.")
            return redirect(self.stocklot.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("inquiries:detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["stocklot"] = self.stocklot
        return context

    def form_valid(self, form):
        form.instance.stocklot = self.stocklot
        form.instance.buyer = self.request.user
        form.instance.seller_company = self.stocklot.company
        messages.success(self.request, "Inquiry sent to the seller.")
        response = super().form_valid(form)
        from core.utils.notifications import create_notification
        from core.models import Notification

        create_notification(
            recipient=self.stocklot.company.owner,
            actor=self.request.user,
            notification_type=Notification.Type.INQUIRY_NEW,
            title=f"New inquiry: {form.instance.display_subject}",
            body=f"Buyer asked about {self.stocklot.title}.",
            url=self.object.get_absolute_url() if hasattr(self.object, "get_absolute_url") else "",
        )
        return response


class SentInquiryListView(LoginRequiredMixin, ListView):
    model = Inquiry
    template_name = "inquiries/inquiry_list_sent.html"
    context_object_name = "inquiries"
    paginate_by = 20

    def get_queryset(self):
        return (
            Inquiry.objects.select_related("stocklot", "seller_company")
            .filter(buyer=self.request.user)
            .order_by("-created_at")
        )


class ReceivedInquiryListView(LoginRequiredMixin, ListView):
    model = Inquiry
    template_name = "inquiries/inquiry_list_received.html"
    context_object_name = "inquiries"
    paginate_by = 20

    def dispatch(self, request, *args, **kwargs):
        try:
            self.company = request.user.company
        except Company.DoesNotExist:
            self.company = None
        if not request.user.is_seller or not self.company:
            messages.info(request, "You need a seller account and company profile to view received inquiries.")
            return redirect("accounts:dashboard")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Inquiry.objects.select_related("stocklot", "buyer", "seller_company")
            .filter(seller_company=self.company, status__in=[Inquiry.Status.APPROVED, Inquiry.Status.REPLIED, Inquiry.Status.CLOSED])
            .order_by("-created_at")
        )


class InquiryDetailView(LoginRequiredMixin, DetailView):
    model = Inquiry
    template_name = "inquiries/inquiry_detail.html"
    context_object_name = "inquiry"

    def get_queryset(self):
        return (
            Inquiry.objects.select_related("stocklot", "buyer", "seller_company")
            .prefetch_related("replies__sender_user", "replies__sender_company")
        )

    def dispatch(self, request, *args, **kwargs):
        inquiry = self.get_object()
        allowed = inquiry.buyer_id == request.user.id
        try:
            company = request.user.company
        except Company.DoesNotExist:
            company = None
        if company and inquiry.seller_company_id == company.id and inquiry.status in [
            Inquiry.Status.APPROVED,
            Inquiry.Status.REPLIED,
            Inquiry.Status.CLOSED,
        ]:
            allowed = True
        if not allowed:
            raise PermissionDenied("You do not have access to this inquiry.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["reply_form"] = InquiryReplyForm()
        context["visible_replies"] = self._get_visible_replies(self.request.user)
        context["show_inquiry_message"] = self._can_see_message(self.object, self.request.user)
        from core.models import DealTrigger

        context["deal"] = DealTrigger.objects.filter(inquiry=self.object).first()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = InquiryReplyForm(request.POST)
        if not self._can_reply(request.user, self.object):
            raise PermissionDenied("You cannot reply to this inquiry.")
        if form.is_valid():
            reply = form.save(commit=False)
            reply.inquiry = self.object
            reply.sender_user = request.user
            company = getattr(request.user, "company", None)
            reply.sender_company = company if company else None
            reply.save()
            # update status when seller replies
            if company and company.id == self.object.seller_company_id and self.object.status == Inquiry.Status.PENDING_ADMIN:
                self.object.status = Inquiry.Status.REPLIED
                self.object.save(update_fields=["status"])
            messages.success(request, "Reply sent.")
            from core.utils.notifications import create_notification
            from core.models import Notification

            if reply.moderation_status == InquiryReply.ModerationStatus.APPROVED:
                recipient = (
                    self.object.buyer if request.user != self.object.buyer else self.object.seller_company.owner
                )
                create_notification(
                    recipient=recipient,
                    actor=request.user,
                    notification_type=Notification.Type.INQUIRY_REPLY,
                    title=f"Reply on inquiry: {self.object.display_subject}",
                    body=reply.message[:180],
                    url=self.object.get_absolute_url() if hasattr(self.object, "get_absolute_url") else "",
                )
            return redirect("inquiries:detail", pk=self.object.pk)
        context = self.get_context_data(object=self.object, reply_form=form)
        return self.render_to_response(context)

    def _can_reply(self, user, inquiry):
        if not user.is_authenticated:
            return False
        if inquiry.buyer_id == user.id:
            return True
        try:
            company = user.company
        except Company.DoesNotExist:
            company = None
        if company and inquiry.seller_company_id == company.id:
            return True
        return False

    def _can_see_message(self, inquiry, viewer):
        if viewer.is_staff:
            return True
        if inquiry.moderation_status == Inquiry.ModerationStatus.APPROVED:
            return True
        if inquiry.moderation_status == Inquiry.ModerationStatus.PENDING_REVIEW and inquiry.buyer_id == viewer.id:
            return True
        return False

    def _get_visible_replies(self, viewer):
        qs = self.object.replies.select_related("sender_user", "sender_company")
        if viewer.is_staff:
            return qs
        return qs.filter(
            Q(moderation_status=InquiryReply.ModerationStatus.APPROVED)
            | (Q(moderation_status=InquiryReply.ModerationStatus.PENDING_REVIEW) & Q(sender_user=viewer))
        )


class InquiryDealAcceptView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        inquiry = get_object_or_404(Inquiry, pk=kwargs["pk"])
        if request.user.id not in [inquiry.buyer_id, inquiry.seller_company.owner_id] and not request.user.is_staff:
            raise PermissionDenied("Not allowed.")
        deal = get_or_create_for_inquiry(inquiry)
        accept_deal(deal, request.user)
        messages.info(request, "Deal acceptance recorded.")
        return redirect("inquiries:detail", pk=inquiry.pk)


class InquiryDealCancelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        inquiry = get_object_or_404(Inquiry, pk=kwargs["pk"])
        if request.user.id not in [inquiry.buyer_id, inquiry.seller_company.owner_id] and not request.user.is_staff:
            raise PermissionDenied("Not allowed.")
        deal = get_or_create_for_inquiry(inquiry)
        cancel_deal(deal, request.user)
        messages.info(request, "Deal cancelled.")
        return redirect("inquiries:detail", pk=inquiry.pk)
