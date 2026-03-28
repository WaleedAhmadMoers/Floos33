from django.contrib.auth import get_user_model

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
    if is_seller:
        deal.seller_accepted = True

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
    return deal


def cancel_deal(deal: DealTrigger, actor):
    if not actor:
        return deal
    deal.status = DealTrigger.Status.CANCELLED
    deal.buyer_accepted = False
    deal.seller_accepted = False
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
    return deal


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
