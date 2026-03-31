from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import CreateView, DetailView, ListView, FormView
from django.db.models import Q

from companies.models import Company
from rfqs.forms import ConversationStartForm, MessageReplyForm, RFQForm
from rfqs.models import RFQ, RFQConversation, RFQFavorite, RFQMessage
from core.utils.deals import accept_deal, cancel_deal, reject_deal, get_or_create_for_rfq_conversation
from core.utils.verification import enforce_verified
from django.views import View


class RFQListView(ListView):
    model = RFQ
    template_name = "rfqs/rfq_list.html"
    context_object_name = "rfqs"
    paginate_by = 20

    def get_queryset(self):
        return (
            RFQ.objects.filter(status=RFQ.Status.OPEN, moderation_status=RFQ.ModerationStatus.APPROVED)
            .select_related("category", "buyer")
            .order_by("-created_at")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context.get("page_obj")
        query = self.request.GET.copy()
        query.pop("page", None)
        base_query = query.urlencode()
        context["pagination_base_query"] = f"&{base_query}" if base_query else ""

        pagination_items = []
        if page_obj and page_obj.paginator.num_pages > 1:
            current = page_obj.number
            total = page_obj.paginator.num_pages
            pages = {1, total, current - 1, current, current + 1}
            if current <= 3:
                pages.update({2, 3, 4})
            if current >= total - 2:
                pages.update({total - 3, total - 2, total - 1})
            pages = sorted(page for page in pages if 1 <= page <= total)

            previous_page = None
            for page in pages:
                if previous_page and page - previous_page > 1:
                    pagination_items.append({"type": "ellipsis"})
                pagination_items.append(
                    {
                        "type": "page",
                        "number": page,
                        "is_current": page == current,
                    }
                )
                previous_page = page

        context["pagination_items"] = pagination_items
        return context


class RFQDetailView(DetailView):
    model = RFQ
    template_name = "rfqs/rfq_detail.html"
    context_object_name = "rfq"

    def dispatch(self, request, *args, **kwargs):
        rfq = self.get_object()
        if rfq.moderation_status != RFQ.ModerationStatus.APPROVED or rfq.status != RFQ.Status.OPEN:
            if not (request.user.is_staff or request.user == rfq.buyer):
                raise Http404("RFQ not available")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ok_seller = False
        if self.request.user.is_authenticated:
            from core.utils.verification import enforce_verified

            ok_seller, _ = enforce_verified(self.request, role="seller")
        ctx["can_quote"] = ok_seller
        ctx["is_saved"] = (
            RFQFavorite.objects.filter(user=self.request.user, rfq=self.object).exists()
            if self.request.user.is_authenticated
            else False
        )
        ctx["response_count"] = self.object.conversations.count()
        ctx["ask_question_url"] = f"{reverse('rfqs:start_conversation', args=[self.object.pk])}?intent=question"
        return ctx


class RFQCreateView(LoginRequiredMixin, CreateView):
    model = RFQ
    form_class = RFQForm
    template_name = "rfqs/rfq_form.html"

    def form_valid(self, form):
        ok, msg = enforce_verified(self.request, role="buyer")
        if not ok:
            messages.error(self.request, msg)
            return redirect("accounts:dashboard")
        form.instance.buyer = self.request.user
        form.instance.moderation_status = RFQ.ModerationStatus.PENDING_REVIEW
        form.instance.status = RFQ.Status.OPEN
        messages.success(self.request, "RFQ submitted and waiting for admin approval.")
        # notify admins
        from core.utils.notifications import create_notification
        from core.models import Notification
        from django.contrib.auth import get_user_model

        for admin in get_user_model().objects.filter(is_staff=True):
            create_notification(
                recipient=admin,
                actor=self.request.user,
                notification_type=Notification.Type.RFQ_NEW_RESPONSE,
                title="New RFQ pending approval",
                body=form.instance.title,
                url="",
            )
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
        rfq = self.object.rfq
        if rfq.moderation_status != RFQ.ModerationStatus.APPROVED or rfq.status != RFQ.Status.OPEN:
            if not (request.user.is_staff or request.user in [self.object.buyer, self.object.seller_user]):
                messages.error(request, "This RFQ is not available.")
                return redirect("rfqs:list")
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

        context["deal"] = get_or_create_for_rfq_conversation(self.object)
        deal = context["deal"]
        if deal:
            from core.utils.deals import _identity_status

            buyer_status = _identity_status(deal, "buyer")
            seller_status = _identity_status(deal, "seller")
            is_buyer = self.request.user.id == self.object.buyer_id
            is_seller = self.request.user.id == self.object.seller_user_id
            buyer_real = deal.buyer.full_name or deal.buyer.email
            seller_real = deal.seller_company.name
            staff = self.request.user.is_staff
            # what viewer can see
            if is_buyer or staff:
                display_buyer = buyer_real
            elif buyer_status == "revealed":
                display_buyer = buyer_real
            else:
                display_buyer = f"Buyer ID #{deal.buyer_id}"

            if is_seller or staff:
                display_seller = seller_real
            elif seller_status == "revealed":
                display_seller = seller_real
            else:
                display_seller = f"Seller ID #{deal.seller_user_id}"
            context["identity_status"] = {"buyer": buyer_status, "seller": seller_status}
            context["identity_labels"] = {"buyer": display_buyer, "seller": display_seller}
        context["can_interact"], _ = enforce_verified(self.request, role="buyer" if self.request.user == self.object.buyer else "seller")
        user = self.request.user
        context["can_deal_actions"] = (
            context["can_interact"] and (user.is_staff or user.id in [self.object.buyer_id, self.object.seller_user_id])
        )
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        role = "buyer" if request.user.id == self.object.buyer_id else "seller"
        ok, msg = enforce_verified(request, role=role)
        if not ok:
            messages.error(request, msg)
            return redirect("rfqs:conversation_detail", pk=self.object.pk)
        form = MessageReplyForm(request.POST, request.FILES)
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
        ok, msg = enforce_verified(request, role="seller")
        if not ok:
            messages.error(request, msg)
            return redirect("rfqs:list")
        self.rfq_obj = get_object_or_404(RFQ, pk=kwargs["pk"], status=RFQ.Status.OPEN)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["rfq"] = self.rfq_obj
        ctx["intent"] = "question" if self.request.GET.get("intent") == "question" else "quote"
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


class RFQFavoriteToggleView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        rfq = get_object_or_404(
            RFQ,
            pk=kwargs.get("pk"),
            status=RFQ.Status.OPEN,
            moderation_status=RFQ.ModerationStatus.APPROVED,
        )
        favorite, created = RFQFavorite.objects.get_or_create(user=request.user, rfq=rfq)
        if not created:
            favorite.delete()
            messages.info(request, "Removed from saved RFQs.")
        else:
            messages.success(request, "RFQ saved.")

        if request.headers.get("HX-Request") or request.headers.get("Accept", "").startswith("application/json"):
            return JsonResponse({"saved": created, "is_saved": created})
        return redirect(rfq.get_absolute_url())


class ConversationDealAcceptView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        convo = get_object_or_404(RFQConversation, pk=kwargs["pk"])
        if request.user.id not in [convo.buyer_id, convo.seller_user_id] and not request.user.is_staff:
            messages.error(request, "Not allowed.")
            return redirect("rfqs:conversation_detail", pk=convo.pk)
        role = "buyer" if request.user.id == convo.buyer_id else "seller"
        ok, msg = enforce_verified(request, role=role)
        if not ok:
            messages.error(request, msg)
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
        role = "buyer" if request.user.id == convo.buyer_id else "seller"
        ok, msg = enforce_verified(request, role=role)
        if not ok:
            messages.error(request, msg)
            return redirect("rfqs:conversation_detail", pk=convo.pk)
        deal = get_or_create_for_rfq_conversation(convo)
        cancel_deal(deal, request.user)
        messages.info(request, "Deal cancelled.")
        return redirect("rfqs:conversation_detail", pk=convo.pk)


class ConversationDealRejectView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        convo = get_object_or_404(RFQConversation, pk=kwargs["pk"])
        if request.user.id not in [convo.buyer_id, convo.seller_user_id] and not request.user.is_staff:
            messages.error(request, "Not allowed.")
            return redirect("rfqs:conversation_detail", pk=convo.pk)
        role = "buyer" if request.user.id == convo.buyer_id else "seller"
        ok, msg = enforce_verified(request, role=role)
        if not ok:
            messages.error(request, msg)
            return redirect("rfqs:conversation_detail", pk=convo.pk)
        deal = get_or_create_for_rfq_conversation(convo)
        reject_deal(deal, request.user)
        messages.info(request, "Deal rejected.")
        return redirect("rfqs:conversation_detail", pk=convo.pk)
