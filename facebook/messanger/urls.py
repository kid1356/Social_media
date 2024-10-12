from django.urls import path
from .views import *



urlpatterns = [
    path('create-message/',MessageCreateView.as_view(), name = 'created-messages'),
    path('receive-message/',ReceiverView.as_view(), name = 'received-messages'),
    path('delete-message/<int:id>',DeleteMessageView.as_view(), name = 'delete-messages'),
    path('get-user-all-chat-rooms',GetRoomInfo.as_view(), name='user-chat-rooms'),
    path('api/private-chat/<int:user_id>/', PrivateChatInitView.as_view(), name='private-chat-init'),
    path('get/<str:room_name>/chats/',GetAllRoomChatView.as_view(), name = "get-room-chat"),

    #front-end url
    path('chat/<str:room_name>/', Group_private_chat_view, name='chat'),

]

