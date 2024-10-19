from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from .models import Comment, Blogs, Notification,Followers
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from user.models import User

@receiver(post_save, sender=Comment)
def comment_created(sender, instance, created, **kwargs):
    if created:
        blog = instance.blog
        user = blog.user
        message = f"{instance.user.first_name} commented on your post."
        notification = Notification.objects.create(user=user, message=message)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{user.id}",
            {
                "type": "send_notification",
                "notification": notification.message
            }
        )

@receiver(m2m_changed, sender=Blogs.likes.through)
def like_post(sender, instance, action, reverse,pk_set,**kwargs):
    if action == "post_add":

        liker_user_id = list(pk_set)[0]
        print("pk.............",pk_set)
        print("like...........................",liker_user_id)
        liker_user = User.objects.get(id=liker_user_id)

        user = instance.user
        message = f"{liker_user.first_name} liked your post."
        notification = Notification.objects.create(user=user, message=message)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user.id}',
            {
                'type': 'send_notification',
                'notification': notification.message
            }
        )


@receiver(post_save, sender =Followers)
def follow_request(sender, created,instance, **kwargs):
    if created and instance.status == 'pending':
        follower = instance.user
        user = instance.followed_user
        message = f"{follower.first_name} sent following request"

        notification = Notification.objects.create(user=user, message =message)
       
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user.id}',
            {
                'type' : 'send_notification',
                'notification' : notification.message
            }
        )

@receiver(post_save, sender= Followers)
def accept_follow_request(sender, created, instance, **kwargs):
    if not created and instance.status == 'accepted':
        follower = instance.user
        followed_user = instance.followed_user 

        message = f'{followed_user.first_name} has accepted your follow request'

        notification = Notification.objects.create(user = follower, message=message)
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send(
            f'notifications_{follower.id}',
            {
                'type':'send_notification',
                'notification': notification.message

            }
        ))



@receiver(post_save, sender = Blogs)
def blog_post(sender, created, instance, **kwargs):
    if created:
        message = "Your blog has been posted Successfully!"
        user = instance.user
        print(user)

        notification = Notification.objects.create(user=user, message=message)

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'notifications_{user.id}',
            {
                'type': 'send_notification',
                'notification': notification.message
            }
        )
