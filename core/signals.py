from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from core.models import Notification
from core.utils.notifications import create_notification
from inquiries.models import Inquiry, InquiryReply
from rfqs.models import RFQ, RFQConversation, RFQMessage
from stocklots.models import Stocklot


def _was_approved(instance, update_fields=None):
    if instance.pk is None:
        return instance.moderation_status == instance.ModerationStatus.APPROVED
    if update_fields and "moderation_status" not in update_fields:
        return False
    model = instance.__class__
    prev = model.objects.filter(pk=instance.pk).values("moderation_status").first()
    if not prev:
        return instance.moderation_status == instance.ModerationStatus.APPROVED
    return prev["moderation_status"] != instance.ModerationStatus.APPROVED and instance.moderation_status == instance.ModerationStatus.APPROVED


@receiver(post_save, sender=Inquiry)
def notify_new_inquiry(sender, instance, created, **kwargs):
    if created:
        create_notification(
            recipient=instance.seller_company.owner,
            actor=instance.buyer,
            notification_type=Notification.Type.INQUIRY_NEW,
            title=f"New inquiry: {instance.display_subject}",
            body=f"A buyer asked about {instance.stocklot.title}.",
            url=instance.get_absolute_url() if hasattr(instance, "get_absolute_url") else "",
        )


@receiver(post_save, sender=InquiryReply)
def notify_inquiry_reply(sender, instance, created, **kwargs):
    if not _was_approved(instance, update_fields=kwargs.get("update_fields")):
        return
    other = instance.inquiry.buyer if instance.sender_user_id != instance.inquiry.buyer_id else instance.inquiry.seller_company.owner
    create_notification(
        recipient=other,
        actor=instance.sender_user,
        notification_type=Notification.Type.INQUIRY_REPLY,
        title=f"New reply on inquiry: {instance.inquiry.display_subject}",
        body=instance.message[:180],
        url=instance.inquiry.get_absolute_url() if hasattr(instance.inquiry, "get_absolute_url") else "",
    )


@receiver(post_save, sender=RFQMessage)
def notify_rfq_message(sender, instance, created, **kwargs):
    if not _was_approved(instance, update_fields=kwargs.get("update_fields")):
        return
    convo = instance.conversation
    if instance.sender_user_id == convo.buyer_id:
        recipient = convo.seller_user
    else:
        recipient = convo.buyer
    create_notification(
        recipient=recipient,
        actor=instance.sender_user,
        notification_type=Notification.Type.RFQ_NEW_RESPONSE,
        title=f"New RFQ message: {convo.rfq.title}",
        body=instance.message[:180],
        url=reverse_cached("rfqs:conversation_detail", convo.pk),
    )


@receiver(post_save, sender=Stocklot)
def notify_listing_approved(sender, instance, created, **kwargs):
    if created:
        return
    if kwargs.get("update_fields") and "status" not in kwargs["update_fields"]:
        return
    if instance.status == Stocklot.Status.APPROVED:
        create_notification(
            recipient=instance.company.owner,
            actor=None,
            notification_type=Notification.Type.LISTING_APPROVED,
            title=f"Listing approved: {instance.title}",
            body="Your stocklot was approved for the marketplace.",
            url=instance.get_absolute_url(),
        )


@receiver(post_save, sender=RFQ)
def notify_rfq_open(sender, instance, created, **kwargs):
    if created:
        return
    if kwargs.get("update_fields") and "status" not in kwargs["update_fields"]:
        return
    if instance.status == RFQ.Status.OPEN:
        create_notification(
            recipient=instance.buyer,
            actor=None,
            notification_type=Notification.Type.RFQ_APPROVED,
            title=f"RFQ approved: {instance.title}",
            body="Your RFQ is now live.",
            url=instance.get_absolute_url(),
        )


# helper to avoid importing reverse in multiple places
from django.urls import reverse  # noqa: E402


def reverse_cached(name, pk):
    try:
        return reverse(name, args=[pk])
    except Exception:
        return ""
