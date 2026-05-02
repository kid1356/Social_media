import json
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Messages,Room,MessageReadStatus
from django.utils import timezone
from user.models import User
from django.core.files.base import ContentFile
import base64
import os
from cryptography.fernet import Fernet
from messanger.utils import encrypt_message_by_public_key,decrypt_message_by_private_key
from django.core.cache import cache
from asgiref.sync import sync_to_async

import logging


logger = logging.getLogger(__name__)

PRIVATE_ROOM_PREFEIX = 'private_'
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY').encode()




class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.cipher_suite = Fernet(ENCRYPTION_KEY)       
    
    
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs'].get('room_name')    #getting room from url
        self.room_group_name = self.get_room_group_name(self.room_name)    #quering if room is private or group
        self.user = self.scope["user"]
        self.room = await self.get_room(self.room_name)

        if not self.room:
            await self.close()
            return 
        
        if not await self.validate_connection():
            return 
        await self.add_user_to_room()
        await self.accept()
        logger.info(f"User {self.user} connected to room {self.room_name}")
        
        await self.send_unread_message()

           
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
        await cache.aset(
        f"online:{self.user.id}", 1,
        timeout=3600
        )
        await cache.aset(
            f"room:{self.room_name}:{self.user.id}",1,
            timeout=3600
        )
        await self.channel_layer.group_add(self.room_group_name, self.channel_name )



    async def disconnect(self, code):
        await self.remove_user_from_room()
        logger.info(f"User {self.user} disconnected from room {self.room_name}")
        await super().disconnect(code)
    
    async def remove_user_from_room(self):
        await cache.adelete(
            f"room:{self.room_name}:{self.user.id}"
        )

        active_room_count_key = f"active_rooms_count:{self.user.id}"
        count = await cache.aget(active_room_count_key) or 0
        count = max(0, int(count) - 1)
 
        if count == 0:
            await cache.adelete(f"online:{self.user.id}")
            await cache.adelete(active_room_count_key)
        else:
            await cache.aset(active_room_count_key, count, timeout=3600)
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    
    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)    #receiving message
            message = text_data_json.get('message',None)
            file_data = text_data_json.get('file',None)
            file_name = text_data_json.get('fileName',None)
            latitude = text_data_json.get('latitude',None)
            longitude = text_data_json.get('longitude',None)


            if file_data and "chunk_index" in text_data_json and "total_chunks" in text_data_json:
                chunk_index = int(text_data_json['chunk_index'])
                total_chunks = int(text_data_json['total_chunks'])
                identifier = file_name or "default_file"
                mime_type = text_data_json.get('mime_type','application/octet-stream')

                cache_key = f'file_chunks_{self.user.id}_{identifier}'
                chunks_data = await sync_to_async(cache.get)(cache_key)
                if not chunks_data:
                    chunks_data = {'total': total_chunks, 'chunks': {}, 'mime_type':mime_type}
                else:
                    if 'mime_type' not in chunks_data:
                        chunks_data['mime_type'] = mime_type

                # Store the chunk after stripping extra whitespace.
                chunks_data['chunks'][chunk_index] = file_data.strip()
                await sync_to_async(cache.set)(cache_key, chunks_data, timeout=300)
                logger.info(f"Received chunks {chunk_index + 1}/{total_chunks} for the file {identifier}")


                if len(chunks_data['chunks']) == total_chunks:

                    sorted_indexes = sorted(chunks_data['chunks'].keys())
                    all_data = ''.join([chunks_data['chunks'][i] for i in sorted_indexes])
                    mime_type = chunks_data['mime_type']


                    full_file_data = f'data:{mime_type};base64,{all_data}'
                    await sync_to_async(cache.delete)(cache_key)
                    file_data = full_file_data

                    try:
                        decoded_data = base64.b64decode(all_data)
                        logger.info(f"Successfully decoded data of length: {len(decoded_data)}")
                    except Exception as e:
                        logger.error(f"Error decoding data: {str(e)}")
                else:
                    return  


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
            symmetric_key = Fernet.generate_key()
            cipher_suite = Fernet(symmetric_key)
            encrypted_message = cipher_suite.encrypt(json.dumps(data).encode())

            encrypted_key = encrypt_message_by_public_key(receiver_public_key['public_key'],symmetric_key.decode())
            
        except Exception as e:
            logger.error(f'Encryption error in private message {e}')
            return 
        
        save_message = await self.save_message(data)
        await self.update_read_status(save_message)
        await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "encrypt_message": encrypted_message,
                    "encrypted_key":encrypted_key,
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
            await self.create_read_status(member,message)
        
        await self.mark_message_as_read(self.user,message)

        for member in room_members:
            if member.id == self.user.id:
                continue
            if await self.user_isOnline(member.id) and await self.is_user_in_room(member.id):
                await self.mark_message_as_read(member, message)


    async def chat_message(self, event):
        encrypted_msg = event["encrypt_message"]
        
        members = event["members"]

        if self.room.room_type == 'private': #Asymmetric decryption
            encrypted_key = event["encrypted_key"]
            private_key = await self.get_receiver_private_key(members['receiver_id'])
            try:
                decrypted_symmetric_key = decrypt_message_by_private_key(private_key,encrypted_key)
                
                cipher_suite = Fernet(decrypted_symmetric_key)
                decrypted_data = cipher_suite.decrypt(encrypted_msg)

                decrypted_message = json.loads(decrypted_data.decode())

            except Exception as e:
                logger.error(f'Decryption error in private message{e}')
                return 
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
        if not unread_messages:
            return
        
        members = await self.get_room_members_name(self.room,self.user)

        for data in unread_messages:
            await self.send(text_data=json.dumps(                       
                        {
                            "message": data,
                            "members":members
                            
                        }))

        await self.mark_all_read(self.user.id, self.room.id)



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


    async def user_isOnline(self,user_id):
        results = await cache.aget(
            f"online:{user_id}"
        )
        return results is not None

    async def is_user_in_room(self, user_id):
        result = await cache.aget(
            f"room:{self.room_name}:{user_id}"
        )
        return result is not None

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
            extention = file_format.split('/')[-1]
            file_name = data['file_name'] or f'default_file.{extention}'
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
               
        messages = Messages.objects.filter(
            room_id=room_id,
            read_statuses__user_id=user_id,
            read_statuses__is_read=False
        ).select_related('sender').order_by('time_stamp')
        result = []
        for msg in messages:
            result.append({
                "text": msg.text,
                "sender_id": msg.sender.id,
                "sender_name": msg.sender.first_name,
                "file": msg.file.url if msg.file else None,
                "file_name": msg.file.name if msg.file else None,
                "latitude": msg.latitude if msg.latitude else None,
                "longitude": msg.longitude if msg.longitude else None,
            })
        return result
    
    @database_sync_to_async
    def mark_all_read(self,user_id, room_id):
        MessageReadStatus.objects.filter(
            user_id=user_id,
            message__room_id = room_id,
            is_read = False
        ).update(is_read=True, read_at = timezone.now())

    @database_sync_to_async
    def mark_message_as_read(self, user, message):
        MessageReadStatus.objects.update_or_create(user=user, message=message,
                                                   defaults={'is_read':True,'read_at':timezone.now()})

    @database_sync_to_async
    def create_read_status(self, user, message):
        MessageReadStatus.objects.get_or_create(user=user, message=message, defaults={'is_read': False})

        