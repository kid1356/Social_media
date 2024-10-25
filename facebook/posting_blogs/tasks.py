from celery import shared_task
from django.utils import timezone
from .models import Story

@shared_task
def mark_story_expired():
    story = Story.objects.filter(expire_at__gt = timezone.now(), is_expired = False)
    story.update(is_expired = True)

@shared_task
def delete_expired_stories():
    time_to_delete = timezone.now() - timezone.timedelta(days=20)
    story = Story.objects.filter(is_expired = True, expire_at__lt = time_to_delete)
    story.delete()