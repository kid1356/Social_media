import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from posting_blogs.models import Notification



online_user = set()
class NotificationConsumer(AsyncWebsocketConsumer):
    
    async def connect(self):
        self.user = self.scope["user"]
        if not self.user.is_authenticated:
            await self.close()
            return "not authenticated"
        

        online_user.add(self.user.id)

        print("online user..........",online_user)

        self.group_name = f"notifications_{self.user.id}"

        
        print(f"User {self.user} connected to room {self.group_name}")
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        
        await self.accept()
        
        try:
            unread_notification = await self.get_unread_notification()
            if unread_notification:
                print("unread_________", unread_notification)


                for notification in unread_notification:
        
                    await self.send(text_data=json.dumps({

                        "notification": notification.message
                    }))
            
                await self.mark_as_read()
            else:
                print("no notification")
        except Exception as e:
            print(f"error {e}")



    async def disconnect(self, code):

        if self.user.id in online_user:
            online_user.remove(self.user.id)


        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )
        return await super().disconnect(code)
    


    async def send_notification(self, event):
        notification = event["notification"]
        
        await self.send(text_data=json.dumps(
            {
                "notification": notification
            }
        ))



        if self.is_user_online(self.user.id):
            await self.mark_as_read()
        
        
    
    @database_sync_to_async
    def get_unread_notification(self):
        return list(Notification.objects.filter(user=self.user, is_read = False).order_by('timestamp'))
    
    @database_sync_to_async
    def mark_as_read(self):
        return Notification.objects.filter(user = self.user, is_read = False).update(is_read = True)
    
    def is_user_online(self, user_id):
        if user_id in online_user:
            return True
        else:
            return False