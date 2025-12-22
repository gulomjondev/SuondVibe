# posts/services/notify.py
from posts.models import Notification


def create_notification(user, actor, type, text, object_id=None, send_notification_task=None):
    notification = Notification.objects.create(
        user=user,
        actor=actor,
        type=type,
        text=text,
        object_id=object_id
    )
    send_notification_task.delay(notification.id)
