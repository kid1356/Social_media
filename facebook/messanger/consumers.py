import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Messages,Room,MessageReadStatus
from django.utils import timezone
from user.models import User
import os
from cryptography.fernet import Fernet
from django.core.files.base import ContentFile
import base64
from messanger.utils import *
# from asgiref.sync import async_to_sync

online_users = set()
room_users = {}
class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.key = os.getenv('ENCRYPTION_KEY').encode()  #getting encription key
        self.cipher_suite = Fernet(self.key)       
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')    #getting room from url
       
        self.room_group_name = self.get_room_group_name(self.room_name)    #quering if room is private or group
        self.user = self.scope["user"]



        if not self.user.is_authenticated:
            await self.close()             #authenticated user only
            return "not authenticated"
        
        online_users.add(self.user.id)

        if self.room_name not in room_users:
            room_users[self.room_name] = set()
        room_users[self.room_name].add(self.user.id)       #adding users to set when they are online
        
        print("online_______room__",room_users)
        
        print("userss.............",online_users)

        if not await self.is_user_allowed_in_room(self.room_name, self.user):
            await self.close()             #if user allowed in private room
            return  "You are not allowed in this room"
        

        if not await self.room_exists(self.room_name):
            
            await self.close()
            print("room does not exist")
        
        await self.join_existing_room(self.room_name)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name ) #adding group 
           
        print(f"User {self.user} connected to room {self.room_name}")
        await self.accept()
 
        try:
            room_name = await self.get_room(self.room_name)
            if self.room_name.startswith('private_'):   #see if room private or Group
                all_messages = await self.get_unread_messages(self.user.id,room_name.id)  
    
            else:
                all_messages = await self.get_unread_messages(self.user.id,room_name.id)
          

            if not all_messages:
                print("No messages found")
            else:
                print(f"Found {len(all_messages)} messages")
            
            for message in all_messages:
                
               
                await self.send_unread_message(message)  # Send the unread message
                await self.mark_message_as_read(self.user,message)  #  mark as read

        except Exception as e:
             print(f"Error processing messages: {e}")




    async def disconnect(self, code):


        if self.room_name in room_users:
            room_users[self.room_name].discard(self.user.id)   
        if self.user.id in online_users:
            online_users.remove(self.user.id)     #removing user from set when they disconnect
        
        print(f"User {self.user.id} disconnected from room {self.room_name}")
        
        # Remove the user from room when they disconnect
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

        await super().disconnect(code)
    
    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)    #receiving message
        message = text_data_json.get('message',None)
        file_data = text_data_json.get('file',None)
        file_name = text_data_json.get('fileName', None)

        latitude = text_data_json.get('latitude',None)
        longitude = text_data_json.get('longitude',None)

         
        data_to_encrypt = {
            "sender":self.user.id,
            "sender_name":self.user.first_name,
            "text": message,
            "file": file_data,
            "file_name": file_name,
            "latitude": latitude,
            "longitude": longitude,
    }
       
        # encrypting the received message
        try:
            encrypted_message = self.encrypt_message(data_to_encrypt)
        except Exception as e:
            print(f'Encryption failed: {e}')
            return 
        
        
        if self.room_name.startswith("private_"):
            # parts = self.room_name.split('_')
            # if len(parts) == 3:  # private_<user1_id>_<user2_id>
            #     _, user1_id, user2_id = parts
            #     if str(self.user.id) == user1_id:
            #         receiver_id = user2_id
                    
            #     else:
            #         receiver_id = user1_id
                    
            #     print('receiver_id_____________',receiver_id) 
        
            
            # print("...............",receiver_user, self.room_name)
            room = await self.get_room(self.room_name)
            members  = await self.get_room_members_name(room, self.user)
            for member in members:
                receiver_user_id = member['id']
                receiver_user_name = member['first_name']

            receiver_user=await self.get_user_by_id(receiver_user_id)
            save_message = await self.save_message(self.user, message,file_data,file_name,latitude,longitude)


            if self.user_isOnline(receiver_user_id) and self.room_name in room_users and receiver_user_id in room_users[self.room_name]:
                
                await self.mark_message_as_read(receiver_user, save_message)
            else:
                
                await self.create_read_status(receiver_user, save_message)

                await self.save_message(self.user, message,file_data,file_name,latitude,longitude)

            await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        "type": "chat_message",
                        "encrypt_message": encrypted_message,
                        "receiver": receiver_user_id,
                        "receiver_name": receiver_user_name
                }
            )
        else:
 
            save_message = await self.save_message(self.user, message,file_data,file_name,latitude=latitude,longitude=longitude)
            room = await self.get_room(self.room_name)

            room_members = await self.get_room_members(room)
            print("room_memers", room_members)

            room_receivers  = await self.get_room_members_name(room,self.user)

            for member in room_members:
                await self.create_read_status(member, save_message)

            for member in room_members:
                if self.user_isOnline(member.id) and self.room_name in room_users and member.id in room_users[self.room_name]:
                    
                    await self.mark_message_as_read(member, save_message)
           


            await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message",
                            "encrypt_message": encrypted_message,
                            "members": room_receivers
                            
                    }
                )
        
       
    
    async def chat_message(self, event):
        

        encrypted_message = event["encrypt_message"]
        
        
        try:
            decrypted_message = self.decrypt_message(encrypted_message)
        except Exception as e:
            print(f'Decryption error in chat_message: {e}')
            return
        
        receiver = event.get("receiver_name",None)
        receiver_id = event.get("receiver",None)
        if receiver:
                                                                # Send the decrypted message to the WebSocket client
            await self.send(text_data=json.dumps(                       
                {
                    "message": decrypted_message,
                    "receiver":receiver_id,
                    "receiver_name": receiver
                    
                }
            ))
        else:
            members = event['members']
            await self.send(text_data=json.dumps(
                {
                    "message": decrypted_message,
                    "members":members
                   
                    
                }
            ))


    async def send_unread_message(self,message):                # sending unread messages to web socket
        
        
        data_to_encrypt = {
            "text": await self.get_message_text(message),  # Get the message text
            "sender_id": await self.get_sender_id(message),
            "sender_name": await self.get_sender_name(message),
            
            "file": await self.get_message_file(message),  # Get the file URL if it exists
            "file_name": message.file.name if message.file else None,  # Get the file name
            "latitude": message.latitude if message.latitude else None,
            "longitude": message.longitude if message.longitude else None,
    }
        
        encrypted_message = self.encrypt_message(data_to_encrypt) 
        
        
        decrypted_message = self.decrypt_message(encrypted_message)
 
        receiver = await self.get_receiver_name(message)
        receiver_id = await self.get_receiver_id(message)
        if receiver:
           await self.send(text_data=json.dumps(                       
                {
                    "message": decrypted_message,
                    'receiver_id':receiver_id,
                    "receiver": receiver
                    
                }
            ))
        else:
            await self.send(text_data=json.dumps(
                {
                    "message": decrypted_message,
                   
                    
                }
            ))



    # encrypt the entire data dictionary
    def encrypt_message(self, data):
        serialized_data = json.dumps(data)
        encrypted_data = self.cipher_suite.encrypt(serialized_data.encode())
        return encrypted_data

    # decrypt the entire data dictionary
    def decrypt_message(self, encrypted_data):
        decrypted_data = self.cipher_suite.decrypt(encrypted_data).decode()
        return json.loads(decrypted_data)
          

    def get_room_group_name(self, room_name):
        if room_name.startswith("private_"):
            return f"private_chat_{room_name}"     #getting group or private rooms
        return f"chat_{room_name}"


    def user_isOnline(self,user_id):
        if user_id in online_users:
            return True                     # checking if user is in set()
        else:
            return False



    @database_sync_to_async
    def is_user_allowed_in_room(self, room_name, user):
        if room_name.startswith("private_"):
            parts = room_name.split('_')                              #checking the user is allowed in room also is user is authenticated
            if len(parts) == 3:
                _, user1_id, user2_id = parts
                allowed_users = {int(user1_id), int(user2_id)}
                return user.id in allowed_users
        return True

    @database_sync_to_async
    def save_message(self, user, message,file_data,file_name,latitude = None,longitude = None):
        receiver = None
        chat_type = 'group'
        file = None
        
        
        if file_data:
            file_format, filestr = file_data.split(';base64,')
            extension = file_format.split('/')[-1]
            original_file_name = file_name if file_name else f'default_file.{extension}'

            file = ContentFile(base64.b64decode(filestr), name=original_file_name)

        if self.room_name.startswith("private_"):
            parts = self.room_name.split('_')
            if len(parts) == 3:  
                _, user1_id, user2_id = parts
                if str(user.id) == user1_id:
                    receiver_id = user2_id
                else:
                    receiver_id = user1_id
                
                try:
                    receiver = User.objects.get(id=receiver_id)
                except User.DoesNotExist:
                   
                    return "no receiver found"
                chat_type = 'private'
            else:
                
                return "room format is not proper or not found"
            
        
        try:
            room = Room.objects.get(name= self.room_name)

            print("room exist_______", room)
        except Room.DoesNotExist:
            room =  Room.objects.create(name = self.room_name, room_type = chat_type) 

            print("room created_______", room)

             #saving the mesasges in the database
        message  =Messages.objects.create(
            sender=user,
            receiver=receiver,
            text=message,
            room = room,
            file = file,
            latitude=latitude,
            longitude=longitude

        )
        return message


    @database_sync_to_async
    def add_user_in_room(self,room_name,room,room_type):
        if room_type=='private':
            _,user1,user2 = room_name.split('_')

            user1 = User.objects.get(id =user1)
            user2 = User.objects.get(id  = user2)

            room.members.add(user2,user1)
        else:
            room.members.add(self.user)

        room.save()

    @database_sync_to_async
    def room_exists(self,room_name):           #checking room exist or not
        return Room.objects.filter(name=room_name).exists()

    @database_sync_to_async
    def join_existing_room(self,room_name):
        room = Room.objects.get(name = room_name)
        room.members.add(self.user)
        room.save()
        return room
    
    
    @database_sync_to_async
    def get_room(self, room):
        return Room.objects.get(name = room)
        
    @database_sync_to_async
    def get_room_members(self,room):
        return list(room.members.all())
    
    @database_sync_to_async
    def get_room_members_name(self,room, sender):
        room_members = list(room.members.exclude(id = sender.id))
        return [{
            'id':user.id,
            'first_name':user.first_name
        } for user in room_members]

    @database_sync_to_async
    def get_unread_messages(self, user_id, room_id):   
        user = User.objects.get(id=user_id)        
        messages = list(Messages.objects.filter(
            room_id=room_id,
            read_statuses__user=user,
            read_statuses__is_read=False
        ).order_by('time_stamp'))
        return messages
    
    @database_sync_to_async
    def mark_message_as_read(self, user, message):
        read_status, created = MessageReadStatus.objects.get_or_create(user=user, message=message)
        if not read_status.is_read:
            read_status.is_read = True
            read_status.read_at = timezone.now()  
            read_status.save()

    @database_sync_to_async
    def create_read_status(self, user, message):
        MessageReadStatus.objects.get_or_create(user=user, message=message, defaults={'is_read': False})

    @database_sync_to_async
    def get_sender_name(self, message):     
        return message.sender.first_name
    
    @database_sync_to_async
    def get_sender_id(self, message):      
        return message.sender.id
       
    @database_sync_to_async
    def get_receiver_name(self, message):    
        if message.receiver:
            return message.receiver.first_name
        else:
            return None
   
    @database_sync_to_async
    def get_receiver_id(self, message):    
        if message.receiver:
            return  message.receiver.id
        else:
            return None

    @database_sync_to_async
    def get_message_text(self, message):    # getting the sender message
        return message.text
   


    @database_sync_to_async
    def get_message_file(self,message):
        return message.file.url if message.file else None



    @database_sync_to_async
    def get_user_by_id(self,user_id):       #getting user by id 
        try:
            user = User.objects.get(id = user_id)     
            return user
        except User.DoesNotExist:
            return None

        
