from core.models import Notification


def notifications(request):
    if request.user.is_authenticated:
        unread = Notification.objects.filter(recipient=request.user, is_read=False).count()
    else:
        unread = 0
    return {"notifications_unread_count": unread}
