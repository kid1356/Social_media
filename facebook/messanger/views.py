from django.shortcuts import render
from .serializers import *
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from .utils import generate_private_room_name
from user.models import User
from rest_framework.pagination import PageNumberPagination
from django.db.models import Max

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
        
        messages = Messages.objects.filter(room = rooms).order_by('time_stamp')
      
        if messages.exists():
            paginator = PageNumberPagination()
            paginator.page_size = 15
            result =paginator.paginate_queryset(messages, request)

            serializer = MessageSerializer(result, many = True)

            return Response(paginator.get_paginated_response(serializer.data).data, status=status.HTTP_200_OK)
        
        else:
            return Response("No Chat Messages found", status=status.HTTP_404_NOT_FOUND)



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

    def get(self, request, user_id, *args, **kwargs):
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        other_user = User.objects.filter(id=user_id).first()
        if not other_user:
            return Response({"error": "User does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        room_name = generate_private_room_name(request.user.id, other_user.id)
        return Response({"room_name": room_name})