from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import Messages


@shared_task
def delete_message_from_DB():
    one_month = timezone.now() - timedelta(days=30)
    msg = Messages.objects.filter(delete_at__lte = one_month)
    count = msg.count()
    msg.delete()
    return f'{count} messages deleted from DB'