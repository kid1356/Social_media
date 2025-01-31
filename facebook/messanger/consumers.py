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
from messanger.utils import encrypt_message_by_public_key,decrypt_message_by_private_key
import logging


logger = logging.getLogger(__name__)

PRIVATE_ROOM_PREFEIX = 'private_'
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY').encode()

online_users = set()
room_users = {}


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.cipher_suite = Fernet(ENCRYPTION_KEY)       
    
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')    #getting room from url
        self.room_group_name = self.get_room_group_name(self.room_name)    #quering if room is private or group
        self.user = self.scope["user"]
        self.room = await self.get_room(self.room_name)

        
        await self.add_user_to_room()
        await self.accept()
        logger.info(f"User {self.user} connected to room {self.room_name}")
        
        await self.send_unread_message()

        logger.info(f"online_______room__{room_users}")
        
        logger.info(f"userss.............{online_users}")
           
    async def validate_connection(self):
        if not self.user.is_authenticated or not await self.is_user_allowed_in_room(self.user, self.room_name):
            logger.warning(f"Unauthorized access attempt by user {self.user}")
            await self.close()
            return False
        if not await self.room_exists(self.room_name):
            await self.close()
            logger.info("room does not exist")
            return False
        return True
   

    async def add_user_to_room(self):
        online_users.add(self.user.id)
        room_users.setdefault(self.room_name, set()).add(self.user.id)
        await self.channel_layer.group_add(self.room_group_name, self.channel_name )



    async def disconnect(self, code):
        await self.remove_user_from_room()
        logger.info(f"User {self.user} disconnected from room {self.room_name}")
        await super().disconnect(code)
    
    async def remove_user_from_room(self):
        if self.room_name in room_users:
            room_users[self.room_name].discard(self.user.id)   
        if self.user.id in online_users:
            online_users.remove(self.user.id)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    
    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)    #receiving message
            message = text_data_json.get('message',None)
            file_data = text_data_json.get('file',None)
            file_name = text_data_json.get('fileName', None)

            latitude = text_data_json.get('latitude',None)
            longitude = text_data_json.get('longitude',None)

            
            data_to_encrypt = {
                "sender_id":self.user.id,
                "sender_name":self.user.first_name,
                "text": message,
                "file": file_data,
                "file_name": file_name,
                "latitude": latitude,
                "longitude": longitude,
        }
            if self.room.room_type=='private':
                await self.handle_private_messages(data_to_encrypt)
            else:
                await self.handle_group_messages(data_to_encrypt)   
        except Exception as e:
            logger.error(f'Error in receive message {e}')

        
    async def handle_private_messages(self, data):
        receiver_public_key = await self.get_receipent_key_private_room(self.room, self.user)
        try:
            encyrpt_msg = encrypt_message_by_public_key(receiver_public_key['public_key'],data)
        except Exception as e:
            logger.error(f'Encryption erroe in private message{e}')
        save_message = await self.save_message(data)
        await self.update_read_status(save_message)
        await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "encrypt_message": encyrpt_msg,
                    "members":{
                        'receiver_id':receiver_public_key['receiver_id'],
                        'receiver_name':receiver_public_key['receiver_name']
                    }
                    
            }
        )
                           
    async def handle_group_messages(self,data):
        try:
            encrypted_message = self.encrypt_message(data)
        except Exception as e:
            logger.error(f'Encryption failed in group messages: {e}')
            return 
        save_message = await self.save_message(data)
        await self.update_read_status(save_message)
        room_receiver = await self.get_room_members_name(self.room, self.user)

        await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            "type": "chat_message",
                            "encrypt_message": encrypted_message,
                            "members": room_receiver
                            
                    }
                )
                 
    async def update_read_status(self, message):      
        room_members  = await self.get_room_members(self.room)

        for member in room_members:
                await self.create_read_status(member, message)
        for member in room_members:
            if self.user_isOnline(member.id) and self.room_name in room_users and member.id in room_users[self.room_name]:
                await self.mark_message_as_read(member, message)


    async def chat_message(self, event):
        encrypted_msg = event["encrypt_message"]
        members = event["members"]

        if self.room.room_type == 'private': #Asymmetric decryption
            private_key = await self.get_receiver_private_key(members['receiver_id'])
            try:
                decrypted_message = decrypt_message_by_private_key(private_key,encrypted_msg)
            except Exception as e:
                logger.error(f'Decryption error in private message{e}')
        else: #symmetric decryption
            decrypted_message = self.decrypt_message(encrypted_msg)
        await self.send(text_data=json.dumps(
                {
                    "message": decrypted_message,
                    "members":members
                
                    
                }
            ))


    async def send_unread_message(self):                # sending unread messages to web socket
        unread_messages = await self.get_unread_messages(self.user.id, self.room.id)
        for message in unread_messages:
            data = {
                "text": await self.get_message_text(message),  
                "sender_id": await self.get_sender_id(message),
                "sender_name": await self.get_sender_name(message),
                
                "file": await self.get_message_file(message),  
                "file_name": message.file.name if message.file else None, 
                "latitude": message.latitude if message.latitude else None,
                "longitude": message.longitude if message.longitude else None,
        }
        
            members = await self.get_room_members_name(self.room,self.user)
            await self.send(text_data=json.dumps(                       
                    {
                        "message": data,
                        "members":members
                        
                    }))

            await self.mark_message_as_read(self.user, message)



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
    def is_user_allowed_in_room(self, user,room_name):
        if room_name.startswith("private_"):
            try: 
                _, user1_id, user2_id = room_name.split('_')
                return user.id in {int(user1_id), int(user2_id)}
                 
            except ValueError:
                return False
        return True
            


    @database_sync_to_async
    def save_message(self,data):
        
        file = None
        if data['file']:
            file_format, filestr = data['file'].split(';base64,')
            extension = file_format.split('/')[-1]
            file_name = data['file_name'] or f'default_file.{extension}'
            file = ContentFile(base64.b64decode(filestr), name=file_name)

        receiver = None
        if self.room_name.startswith("private_"):
            _,user1_id,user2_id = self.room_name.split('_')
            receiver_id = user2_id if str(self.user.id) == user1_id else user1_id
            receiver = User.objects.get(id=receiver_id)

        #saving the mesasges in the database
        message  =Messages.objects.create(
            sender=self.user,
            receiver=receiver,
            text=data['text'],
            room = self.room,
            file = file,
            latitude=data['latitude'],
            longitude=data['longitude']

        )
        return message


    @database_sync_to_async
    def room_exists(self,room_name):           #checking room exist or not
        return Room.objects.filter(name=room_name).exists()
    
    
    @database_sync_to_async
    def get_room(self, room):
        try:
            return Room.objects.get(name = room)
        except Room.DoesNotExist:
            logger.error(f'Room with {room} does not exists')
            return None
        
    @database_sync_to_async
    def get_room_members(self,room):
        return list(room.members.all())

    @database_sync_to_async
    def get_room_members_name(self,room, sender):
        room_members = list(room.members.exclude(id = sender.id))
        return [{
            'receiver_id':user.id,
            'receiver_name':user.first_name
        } for user in room_members]

    @database_sync_to_async
    def get_receipent_key_private_room(self,room,sender):
        receiver = room.members.exclude(id=sender.id).first()
        if receiver:
            return {
                "receiver_id":receiver.id,
                "receiver_name":receiver.first_name,
                "public_key":receiver.public_key,
                
            } 
        else:
            return None
        
    @database_sync_to_async
    def get_receiver_private_key(self,user_id):
        try:
            user = User.objects.get(id=user_id)
            return user.private_key
        except Exception as e:
            return e

    @database_sync_to_async
    def get_unread_messages(self, user_id, room_id):   
               
        messages = list(Messages.objects.filter(
            room_id=room_id,
            read_statuses__user_id=user_id,
            read_statuses__is_read=False
        ).select_related('sender').order_by('time_stamp'))
        return messages
    
    @database_sync_to_async
    def mark_message_as_read(self, user, message):
        MessageReadStatus.objects.update_or_create(user=user, message=message,
                                                   defaults={'is_read':True,'read_at':timezone.now()})

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
    def get_message_text(self, message):    # getting the sender message
        return message.text

    @database_sync_to_async
    def get_message_file(self,message):
        return message.file.url if message.file else None


        
