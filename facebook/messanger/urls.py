from django.urls import path
from .views import *



urlpatterns = [
#delete message
    path('delete-message/<int:id>/',DeleteMessageForMeView.as_view(), name = 'delete-messages'),
    path('delete-message-foreveryone/<int:id>/',DeleteMessageForEveryOneView.as_view(), name='delete_message_foreveryone'),
    path('delete-entire-conversation/<int:room_id>/',DeleteEntireConversation.as_view(), name='delete_entire_conversation'),

# Read message
    path('get-user-all-chat-rooms',GetRoomInfo.as_view(), name='user-chat-rooms'),
    path('get/<str:room_name>/chats/',GetAllRoomChatView.as_view(), name = "get-room-chat"),

# create room
    path('create-group/',CreateGroupView.as_view(), name='create-group'),
    path('api/private-chat/<int:user_id>/', PrivateChatInitView.as_view(), name='private-chat-init'),
    path('update/<int:group_id>/add_members/',AddGroupMembersView.as_view(), name='add-members-in-group'),

    #front-end url
    path('chat/<str:room_name>/', Group_private_chat_view, name='chat'),

]

