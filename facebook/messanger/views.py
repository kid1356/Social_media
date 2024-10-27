from django.shortcuts import render
from .serializers import *
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from user.models import User
from rest_framework.pagination import PageNumberPagination


# Create your views here.


def Group_private_chat_view(request,room_name):
    return render(request, 'private_chat.html',{'room_name':room_name})

class MessageCreateView(APIView):
    def post(self, request,*args, **kwargs):
        serializer = MessageSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(sender = request.user)
        
        return Response({"msg created":serializer.data}, status=status.HTTP_201_CREATED)


class GetRoomInfo(APIView):
    permission_classes = [IsAuthenticated]
    def get(self,request):
        
        user =request.user
        try:
            rooms = Room.objects.filter(members = user)
            room_type = request.query_params.get('room_type',None)

            if room_type:
                rooms = rooms.filter(room_type=room_type)
        
 
            paginator =PageNumberPagination()
            paginator.page_size = 15
            result = paginator.paginate_queryset(rooms,request)
            serializer = RoomSerializer(result, many = True, context = {'request':request})

            return Response(paginator.get_paginated_response(serializer.data).data,status=status.HTTP_200_OK)
        except:
            return Response("No Rooms Found",status=status.HTTP_404_NOT_FOUND)



class GetAllRoomChatView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, room_name):
        try:
            rooms = Room.objects.get(name =room_name, members =request.user)
        except Room.DoesNotExist:
            return Response("Room does not exist", status= status.HTTP_404_NOT_FOUND)
        
        messages = Messages.objects.filter(room = rooms).order_by('-time_stamp')
      
        if messages.exists():
            paginator = PageNumberPagination()
            paginator.page_size = 15
            result =paginator.paginate_queryset(messages, request)

            serializer = MessageSerializer(result, many = True)

            return Response(paginator.get_paginated_response(serializer.data).data, status=status.HTTP_200_OK)
        
        else:
            return Response({'result':[]}, status=status.HTTP_200_OK)



class ReceiverView(APIView):
    def get(self, request):
        # Filter messages where the current user is either the sender or receiver
        messages = Messages.objects.filter(models.Q(sender=request.user) | models.Q(receiver=request.user))
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


#Deleting messages
class DeleteMessageView(APIView):
    def delete(self,request,id):
        message = get_object_or_404(Messages, id=id)

        if request.user == message.sender or request.user == message.receiver:
            serializer = MessageSerializer(message)
            msg_deleted = serializer.data
            
            message.delete()
            return Response({"the message is deleted": msg_deleted},status=status.HTTP_200_OK)
    
        else:
            return Response('You are not authorized to do this action', status=status.HTTP_401_UNAUTHORIZED)

              
 
           
        

class PrivateChatInitView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id, *args, **kwargs):
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        other_user = User.objects.filter(id=user_id).first()
        if not other_user:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        sorted_ids = sorted([request.user.id, other_user.id])
        room_name = f"private_{sorted_ids[0]}_{sorted_ids[1]}"

        room, created = Room.objects.get_or_create(name = room_name, defaults={'room_type' : 'private'})
        if created:
            return Response({"room_created":PrivateRoomSerializer(room).data}, status=status.HTTP_201_CREATED)
        else:
          return Response({"room_name": PrivateRoomSerializer(room).data}, status=status.HTTP_200_OK)
    

class CreateGroupView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        
        serializer = GroupRoomSerializer(data = request.data, context = {'user':request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Group is Created":serializer.data}, status=status.HTTP_201_CREATED)

class AddGroupMembersView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self,request, group_id):
        try:
            room = Room.objects.get(id= group_id)
        except Room.DoesNotExist:
         return Response("No room found", status=status.HTTP_404_NOT_FOUND)
    
        if request.user != room.group_admin:
            return Response("Your are not admin of this group",status=status.HTTP_401_UNAUTHORIZED)
        
        if room.room_type != 'group':
            return Response("members can only added in room type group ", status=status.HTTP_400_BAD_REQUEST)
        
        serializer = AddMembersSerializer(room,data = request.data, partial = True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"members added":serializer.data}, status=status.HTTP_200_OK)