from django.contrib.auth import get_user_model
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from core.models import DealTrigger, Notification, DealHistory
from core.utils.notifications import create_notification


def _participants(deal):
    return deal.buyer, deal.seller_user


def _deal_url(deal):
    if deal.inquiry_id:
        try:
            return deal.inquiry.get_absolute_url()
        except Exception:
            return ""
    if deal.rfq_conversation_id:
        from django.urls import reverse

        return reverse("rfqs:conversation_detail", args=[deal.rfq_conversation_id])
    return ""


def _identity_status(deal, target: str):
    """Return identity visibility state for target ('buyer' or 'seller'): revealed | pending | hidden"""
    if target == "seller":
        if deal.seller_identity_revealed:
            return "revealed"
        note_filter = "seller"
    else:
        if deal.buyer_identity_revealed:
            return "revealed"
        note_filter = "buyer"

    last_req = deal.history.filter(action="identity_request", note__icontains=note_filter).order_by("-created_at").first()
    last_dec = deal.history.filter(action="identity_decision", note__icontains=note_filter).order_by("-created_at").first()
    if last_req and (not last_dec or last_req.created_at > last_dec.created_at):
        return "pending"
    return "hidden"


def accept_deal(deal: DealTrigger, actor):
    if not actor:
        return deal
    is_buyer = actor.id == deal.buyer_id
    is_seller = actor.id == deal.seller_user_id
    is_admin = getattr(actor, "is_staff", False)

    if is_admin:
        # admin clicking accept shouldn't change acceptance flags; admin approves via admin panel
        return deal

    if is_buyer:
        deal.buyer_accepted = True
        deal.buyer_rejected = False
    if is_seller:
        deal.seller_accepted = True
        deal.seller_rejected = False

    deal.accepted_by = actor
    if deal.buyer_accepted and deal.seller_accepted:
        deal.status = DealTrigger.Status.MUTUAL
    else:
        deal.status = DealTrigger.Status.PENDING
    deal.save()

    DealHistory.objects.create(deal=deal, actor=actor, action="accepted", note="Participant accepted")

    url = _deal_url(deal)
    buyer, seller = _participants(deal)
    # Notify other party on first accept
    if deal.status == DealTrigger.Status.PENDING:
        other = seller if is_buyer else buyer
        if other:
            create_notification(
                recipient=other,
                actor=actor,
                notification_type=Notification.Type.DEAL_UPDATED,
                title="Deal requested",
                body="The other side accepted the deal. Please confirm if you agree.",
                url=url,
        )
    # Notify admins when mutual acceptance reached
    if deal.status == DealTrigger.Status.MUTUAL:
        admin_users = get_user_model().objects.filter(is_staff=True)
        for admin in admin_users:
            create_notification(
                recipient=admin,
                actor=actor,
                notification_type=Notification.Type.DEAL_UPDATED,
                title="Deal awaiting approval",
                body="A deal reached mutual acceptance and needs admin approval.",
                url=url,
            )
        DealHistory.objects.create(deal=deal, actor=actor, action="mutual_acceptance", note="Both sides accepted")
    _broadcast_deal(deal)
    return deal


def reject_deal(deal: DealTrigger, actor):
    if not actor:
        return deal
    is_buyer = actor.id == deal.buyer_id
    is_seller = actor.id == deal.seller_user_id
    if is_buyer:
        deal.buyer_rejected = True
        deal.buyer_accepted = False
    if is_seller:
        deal.seller_rejected = True
        deal.seller_accepted = False
    deal.status = DealTrigger.Status.REJECTED
    deal.progress_status = DealTrigger.Progress.NOT_STARTED
    deal.save(update_fields=["buyer_rejected", "seller_rejected", "buyer_accepted", "seller_accepted", "status", "progress_status", "updated_at"])
    DealHistory.objects.create(deal=deal, actor=actor, action="rejected", note="Deal rejected by participant")
    url = _deal_url(deal)
    buyer, seller = _participants(deal)
    other = seller if is_buyer else buyer
    if other:
        create_notification(
            recipient=other,
            actor=actor,
            notification_type=Notification.Type.DEAL_UPDATED,
            title="Deal rejected",
            body="The other party rejected the deal.",
            url=url,
        )
    _broadcast_deal(deal)
    return deal


def cancel_deal(deal: DealTrigger, actor):
    if not actor:
        return deal
    deal.status = DealTrigger.Status.CANCELLED
    deal.buyer_accepted = False
    deal.seller_accepted = False
    deal.buyer_rejected = False
    deal.seller_rejected = False
    deal.accepted_by = actor
    deal.save()
    DealHistory.objects.create(deal=deal, actor=actor, action="cancelled", note="Cancelled by participant")
    url = _deal_url(deal)
    buyer, seller = _participants(deal)
    other = seller if actor.id == deal.buyer_id else buyer
    if other:
        create_notification(
            recipient=other,
            actor=actor,
            notification_type=Notification.Type.DEAL_UPDATED,
            title="Deal cancelled",
            body="The other side cancelled the deal request.",
            url=url,
        )
    _broadcast_deal(deal)
    return deal


def _broadcast_deal(deal: DealTrigger):
    channel_layer = get_channel_layer()
    if not channel_layer:
        return
    last_history = deal.history.order_by("-created_at").first()
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
        next_action = "Buyer or seller must accept"
    elif deal.status == DealTrigger.Status.MUTUAL:
        next_action = "Admin approval required"
    elif deal.status == DealTrigger.Status.APPROVED:
        next_action = "Deal approved"
    elif deal.status == DealTrigger.Status.CANCELLED:
        next_action = "Deal cancelled"
    elif deal.status == DealTrigger.Status.REJECTED:
        next_action = "Deal rejected"
    else:
        next_action = ""

    payload = {
        "status": deal.status,
        "status_display": deal.get_status_display(),
        "progress": deal.get_progress_status_display(),
        "buyer_accepted": deal.buyer_accepted,
        "seller_accepted": deal.seller_accepted,
        "buyer_rejected": deal.buyer_rejected,
        "seller_rejected": deal.seller_rejected,
        "buyer_decision": buyer_dec,
        "seller_decision": seller_dec,
        "admin_decision": admin_dec,
        "next_action": next_action,
        "buyer_identity_status": _identity_status(deal, "buyer"),
        "seller_identity_status": _identity_status(deal, "seller"),
        "buyer_real": deal.buyer.full_name or deal.buyer.email,
        "buyer_masked": f"Buyer ID #{deal.buyer_id}",
        "seller_real": deal.seller_company.name,
        "seller_masked": f"Seller ID #{deal.seller_user_id}",
        "latest_event": f"{last_history.note}" if last_history else "",
        "updated": deal.updated_at.isoformat(),
    }
    async_to_sync(channel_layer.group_send)(f"deal_{deal.id}", {"type": "deal.update", "payload": payload})
    if deal.inquiry_id:
        async_to_sync(channel_layer.group_send)(f"inquiry_{deal.inquiry_id}", {"type": "deal.update", "payload": payload})
    if deal.rfq_conversation_id:
        async_to_sync(channel_layer.group_send)(
            f"rfqconv_{deal.rfq_conversation_id}", {"type": "deal.update", "payload": payload}
        )


def get_or_create_for_inquiry(inquiry):
    deal, _ = DealTrigger.objects.get_or_create(
        inquiry=inquiry,
        defaults={
            "deal_type": DealTrigger.DealType.INQUIRY,
            "buyer": inquiry.buyer,
            "seller_company": inquiry.seller_company,
            "seller_user": inquiry.seller_company.owner,
        },
    )
    return deal


def get_or_create_for_rfq_conversation(conversation):
    deal, _ = DealTrigger.objects.get_or_create(
        rfq_conversation=conversation,
        defaults={
            "deal_type": DealTrigger.DealType.RFQ,
            "buyer": conversation.buyer,
            "seller_company": conversation.seller_company,
            "seller_user": conversation.seller_user,
        },
    )
    return deal
