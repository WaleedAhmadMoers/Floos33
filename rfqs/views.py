from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, FormView
from django.db.models import Q

from companies.models import Company
from rfqs.forms import ConversationStartForm, MessageReplyForm, RFQForm
from rfqs.models import RFQ, RFQConversation, RFQMessage
from core.utils.deals import accept_deal, cancel_deal, get_or_create_for_rfq_conversation
from django.views import View


class RFQListView(ListView):
    model = RFQ
    template_name = "rfqs/rfq_list.html"
    context_object_name = "rfqs"
    paginate_by = 20

    def get_queryset(self):
        return (
            RFQ.objects.filter(status=RFQ.Status.OPEN)
            .select_related("category", "buyer")
            .order_by("-created_at")
        )


class RFQDetailView(DetailView):
    model = RFQ
    template_name = "rfqs/rfq_detail.html"
    context_object_name = "rfq"


class RFQCreateView(LoginRequiredMixin, CreateView):
    model = RFQ
    form_class = RFQForm
    template_name = "rfqs/rfq_form.html"

    def form_valid(self, form):
        form.instance.buyer = self.request.user
        messages.success(self.request, "RFQ created successfully.")
        return super().form_valid(form)


class MyRFQListView(LoginRequiredMixin, ListView):
    model = RFQ
    template_name = "rfqs/my_rfqs.html"
    context_object_name = "rfqs"

    def get_queryset(self):
        return RFQ.objects.filter(buyer=self.request.user).select_related("category").order_by("-created_at")


class BuyerConversationListView(LoginRequiredMixin, ListView):
    model = RFQConversation
    template_name = "rfqs/my_conversations_buyer.html"
    context_object_name = "conversations"

    def get_queryset(self):
        return RFQConversation.objects.filter(buyer=self.request.user).select_related("rfq", "seller_company")


class MyResponsesListView(LoginRequiredMixin, ListView):
    model = RFQConversation
    template_name = "rfqs/my_conversations_seller.html"
    context_object_name = "conversations"

    def get_queryset(self):
        return RFQConversation.objects.filter(seller_user=self.request.user).select_related("rfq", "buyer")


class ConversationDetailView(LoginRequiredMixin, DetailView):
    model = RFQConversation
    template_name = "rfqs/conversation_detail.html"
    context_object_name = "conversation"

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not (
            request.user.is_staff
            or request.user == self.object.buyer
            or request.user == self.object.seller_user
        ):
            messages.error(request, "You are not allowed to view this conversation.")
            return redirect("rfqs:list")
        return super().dispatch(request, *args, **kwargs)

    def _visible_messages(self, user):
        qs = self.object.messages.select_related("sender_company", "sender_user")
        if user.is_staff:
            return qs
        return qs.filter(
            Q(moderation_status=RFQMessage.ModerationStatus.APPROVED)
            | Q(sender_user=user, moderation_status=RFQMessage.ModerationStatus.PENDING_REVIEW)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["messages"] = self._visible_messages(self.request.user)
        context["form"] = MessageReplyForm()
        from core.models import DealTrigger

        context["deal"] = DealTrigger.objects.filter(rfq_conversation=self.object).first()
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = MessageReplyForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            msg.conversation = self.object
            msg.sender_user = request.user
            msg.sender_company = getattr(request.user, "company", None)
            msg.moderation_status = RFQMessage.ModerationStatus.PENDING_REVIEW
            msg.save()
            messages.info(request, "Message submitted for admin review.")
            from core.utils.notifications import create_notification
            from core.models import Notification

            recipient = self.object.buyer if request.user != self.object.buyer else self.object.seller_user
            create_notification(
                recipient=recipient,
                actor=request.user,
                notification_type=Notification.Type.RFQ_NEW_RESPONSE,
                title=f"New RFQ message: {self.object.rfq.title}",
                body="A new message was posted (pending admin review).",
                url=reverse("rfqs:conversation_detail", args=[self.object.pk]),
            )
            return redirect("rfqs:conversation_detail", pk=self.object.pk)
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


class ConversationStartView(LoginRequiredMixin, CreateView):
    model = RFQMessage
    form_class = ConversationStartForm
    template_name = "rfqs/conversation_start.html"

    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, "company"):
            messages.error(request, "You need an active company profile to respond.")
            return redirect("companies:create")
        self.rfq_obj = get_object_or_404(RFQ, pk=kwargs["pk"], status=RFQ.Status.OPEN)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["rfq"] = self.rfq_obj
        return ctx

    def form_valid(self, form):
        convo, created = RFQConversation.objects.get_or_create(
            rfq=self.rfq_obj,
            buyer=self.rfq_obj.buyer,
            seller_company=self.request.user.company,
            seller_user=self.request.user,
        )
        msg = form.save(commit=False)
        msg.conversation = convo
        msg.sender_user = self.request.user
        msg.sender_company = self.request.user.company
        msg.moderation_status = RFQMessage.ModerationStatus.PENDING_REVIEW
        msg.save()
        messages.info(self.request, "Quote sent for admin review.")
        from core.utils.notifications import create_notification
        from core.models import Notification

        create_notification(
            recipient=self.rfq_obj.buyer,
            actor=self.request.user,
            notification_type=Notification.Type.RFQ_NEW_RESPONSE,
            title=f"RFQ response started: {self.rfq_obj.title}",
            body="A seller sent a quote (pending admin review).",
            url=reverse("rfqs:conversation_detail", args=[convo.pk]),
        )
        self.success_url = reverse("rfqs:conversation_detail", args=[convo.pk])
        return super().form_valid(form)

    def get_success_url(self):
        return getattr(self, "success_url", reverse("rfqs:list"))


class ConversationDealAcceptView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        convo = get_object_or_404(RFQConversation, pk=kwargs["pk"])
        if request.user.id not in [convo.buyer_id, convo.seller_user_id] and not request.user.is_staff:
            messages.error(request, "Not allowed.")
            return redirect("rfqs:conversation_detail", pk=convo.pk)
        deal = get_or_create_for_rfq_conversation(convo)
        accept_deal(deal, request.user)
        messages.info(request, "Deal acceptance recorded.")
        return redirect("rfqs:conversation_detail", pk=convo.pk)


class ConversationDealCancelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        convo = get_object_or_404(RFQConversation, pk=kwargs["pk"])
        if request.user.id not in [convo.buyer_id, convo.seller_user_id] and not request.user.is_staff:
            messages.error(request, "Not allowed.")
            return redirect("rfqs:conversation_detail", pk=convo.pk)
        deal = get_or_create_for_rfq_conversation(convo)
        cancel_deal(deal, request.user)
        messages.info(request, "Deal cancelled.")
        return redirect("rfqs:conversation_detail", pk=convo.pk)
