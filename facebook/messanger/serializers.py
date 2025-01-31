from .models import *
from rest_framework import serializers
from user.serializers import UserProfileSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    receiver_name = serializers.SerializerMethodField()
    class Meta:
        model = Messages
        fields = ['sender','sender_name','receiver','receiver_name','text','time_stamp','file']

    
    def get_sender_name(self,obj):
        sender = obj.sender
        return sender.first_name if sender else None
    
    def get_receiver_name(self,obj):
        receiver = obj.receiver
        return receiver.first_name if receiver else None
    
class PrivateRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'name','room_type','members']



class RoomSerializer(serializers.ModelSerializer):
    participants = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    last_message_time = serializers.SerializerMethodField()
    unread_messages_count = serializers.SerializerMethodField()
    class Meta:
        model= Room
        fields  = ['id','name','room_type','last_message','last_message_time','unread_messages_count','participants']

    def get_participants(self,obj):
        sender = self.context['request'].user
        participants = obj.members.exclude(id = sender.id).values('id','first_name','profile_picture')
        return participants
    
    def get_last_message(self,obj):
        message = obj.messages.order_by('-time_stamp').first()
        return message.text if message else None
    
    def get_last_message_time(self, obj):
        time = obj.messages.order_by('-time_stamp').first()
        return time.time_stamp if time else None
    
    def get_unread_messages_count(self, obj):
        user = self.context['request'].user
        unread = MessageReadStatus.objects.filter(
            message__room = obj,
            user =user,
            is_read = False
        ).count()
        return unread
    
class GroupRoomSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(many = True, queryset = User.objects.all(), required = True)
    class Meta:
        model = Room
        fields = ['id','name','members']
        read_only_fields = ['id','group_admin','created_at','room_type']
        extra_kwargs = {
            'name':{'required':True},
        }

    def create(self, validate_data):
        group_admin = self.context.get('user')
        members = validate_data.pop('members',[])

        room = Room.objects.create(
                name =validate_data['name'],
                group_admin =group_admin,
                room_type = 'group'
            )
            
        room.members.add(group_admin)
        room.members.add(*members)
        return room
    

class AddMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields =['members']
    
    def update(self, instance, validated_data):
        
        new_members = validated_data.get('members',[])

        instance.members.add(*new_members)
        instance.save()

        return instance

