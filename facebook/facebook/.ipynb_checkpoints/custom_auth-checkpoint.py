from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from user.models import User
from rest_framework_simplejwt.tokens import AccessToken
from channels.db import database_sync_to_async




# class CustomAuthMiddleware(BaseMiddleware):
#     async def __call__(self, scope, receive, send):
#         user = await self.get_user(scope)
#         scope['user'] = user
#         return await super().__call__(scope, receive, send)
    
#     @database_sync_to_async
#     def get_user(self,scope):
#         token = None

#         for key, value in scope['headers']:
#             if key == b'authorization':
#                 token = value.decode().split(' ')[1]
                
#         if token:
#             try:
#                 access_token = AccessToken(token)
#                 user = User.objects.get(id= access_token['user_id'])
#                 return user
#             except User.DoesNotExist:
#                 pass
#         return AnonymousUser()

from channels.db import database_sync_to_async


User_ =User


class CustomAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        user = await self.get_user(scope)
        scope['user'] = user
        return await super().__call__(scope, receive, send)

    @database_sync_to_async
    def get_user(self,scope):
        query_string = str(scope['query_string'].decode('utf-8')).split("=")
        ["token","dlhsgukhsglhfsdlg"]
        # ["token","dlhsgukhsglhfsdlg"]
        token = query_string[1]
        if token:
            try:
                access_token = AccessToken(token)
                user = User.objects.get(id= access_token['user_id'])
                return user
            except User.DoesNotExist:
                pass
        return AnonymousUser()


