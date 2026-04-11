from core.models import Notification


def create_notification(recipient, notification_type, title, body, url="", actor=None):
    if recipient is None:
        return None
    if actor and actor == recipient:
        return None
    return Notification.objects.create(
        recipient=recipient,
        actor=actor,
        notification_type=notification_type,
        title=title,
        body=body,
        url=url or "",
    )
