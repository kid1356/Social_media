from django.db import models
from user.models import User
# Create your models here.


class Room(models.Model):
    ROOM_TYPE = [
        ('private', 'Private'),
        ('group', 'Group')
    ]
    
    name = models.CharField(max_length=200, unique=True)
    members = models.ManyToManyField(User, related_name='rooms')  # Users in the room
    room_type = models.CharField(max_length=200, choices=ROOM_TYPE, default='group')
    group_admin = models.ForeignKey(User,on_delete=models.CASCADE, null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.name}'

    def get_receiver(self, sender):
 
        if self.room_type == 'private' and self.members.count() == 2:

            return self.members.exclude(id=sender.id).first()
        return None

class Messages(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', null=True)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField(max_length=1000, null=True, blank=True)
    file = models.FileField(upload_to='files/', blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    time_stamp = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f'{self.sender} in {self.room}: {self.text[:20]}...'


class MessageReadStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.ForeignKey(Messages, on_delete=models.CASCADE, related_name='read_statuses')
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'message')

    def __str__(self):
        return f'Message {self.message.id} read by {self.user.username}'