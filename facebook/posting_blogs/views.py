from rest_framework import status
from rest_framework.permissions import IsAuthenticated,BasePermission
from rest_framework.response import Response
from adrf.views import APIView
from drf_yasg.utils import swagger_auto_schema
from .serializers import CommentSerializer, BlogSerializer, FollowSerializer, StorySerializer
from posting_blogs.models import Blogs,Comment,Story,Followers
from rest_framework.pagination import PageNumberPagination
from user.serializers import UserProfileSerializer
from user.models import User
from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils import timezone

#custom permissions
class IsOwnerOfBlog(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:  # Can read the object only
            return True

        return obj.user == request.user


# # Create your views here.  
# class Blog_Create_view(APIView):
#     async def post(self, request):
#         try:
#             async with transaction.atomic():
#                 serializer = BlogSerializer(data= request.data)         #posting Blogs 
#                 serializer.is_valid(raise_exception=True)
#                 saved_blog=await sync_to_async(serializer.save)(user = request.user)
#                 blog = await Blogs.objects.select_related('user').aget(id=saved_blog.id)

#                 data = await sync_to_async(lambda: BlogSerializer(blog).data)()
#                 return Response({'The Blogs is Posted':data},status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class Blog_Create_view(APIView):
    @swagger_auto_schema(
            request_body=BlogSerializer,
            responses = {201: BlogSerializer}
    )
    async def post(self, request):
        try:
            @sync_to_async
            def create_blog():
                with transaction.atomic():
                    serializer = BlogSerializer(data=request.data)
                    serializer.is_valid(raise_exception=True)
                    saved_blog = serializer.save(user=request.user)
                    
                    blog = Blogs.objects.select_related('user').get(id=saved_blog.id)
                    
                    return BlogSerializer(blog).data

            data = await create_blog()
            return Response({'The Blog is Posted': data}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
#Getting all blogs or post from a specific User    
class GetAllUserBlogsView(APIView):
    permission_classes = [IsAuthenticated]
    async def get(self,request):

        blogs = await sync_to_async(list)(Blogs.objects.select_related('user').filter(user=request.user).order_by('-created_at'))

        paginator = PageNumberPagination()
        paginator.page_size = 5
        result = await sync_to_async(paginator.paginate_queryset)(blogs,request)
        data = await sync_to_async(lambda: BlogSerializer(result,many =True).data)()

        return Response(paginator.get_paginated_response(data).data,status=status.HTTP_200_OK)
        
    

        

# getting single blogs by id
class Blog_Get_view(APIView):
    permission_classes = [IsAuthenticated]
    async def get(self,request,id):
        try:

            blog = await Blogs.objects.select_related('user').prefetch_related('likes').aget(id=id)
            data = await sync_to_async(lambda: BlogSerializer(blog).data)()    
            return Response({"data":data},status=status.HTTP_200_OK)
        except Blogs.DoesNotExist:
            return Response({"Blog not Found"},status=status.HTTP_404_NOT_FOUND)


# Updating blog 
class Blog_Patch_view(APIView):   

    permission_classes = [IsAuthenticated,IsOwnerOfBlog]

    async def patch(self, request,id):
        try:
            blog = await Blogs.objects.aget(id=id)

            await sync_to_async(self.check_object_permissions)(request,blog)

            serializer = BlogSerializer(blog, data=request.data, partial = True)
        
            await sync_to_async(serializer.is_valid)(raise_exception=True)

            await sync_to_async(serializer.save)()
            updated_blog = await Blogs.objects.select_related('user').prefetch_related('likes').aget(id=id)
            data = await sync_to_async(lambda: BlogSerializer(updated_blog).data)()
            return Response({'updated successfully':data},status=status.HTTP_200_OK)
        except Blogs.DoesNotExist:
            return Response('Blog Does not FOund',status=status.HTTP_404_NOT_FOUND)


#Deleting blog
class DeleteBlogView(APIView):
    permission_classes = [IsAuthenticated,IsOwnerOfBlog]
    async def delete(self, request,id):
        try:
            blog = await Blogs.objects.aget(id=id)
            await sync_to_async(self.check_object_permissions)(request, blog)
            data = await sync_to_async(lambda: BlogSerializer(blog).data)()

            await blog.adelete()
            return Response({"the blog is deleted":data}, status=status.HTTP_200_OK)

        except Blogs.DoesNotExist:
            return Response({"blog Does not found or already deleted"}, status=status.HTTP_400_BAD_REQUEST)




# liking A blog
class Like_Blog_view(APIView):
    permission_classes= [IsAuthenticated]
    async def post(self,request,id):
        user = request.user

        try:
            blog = await Blogs.objects.aget(id=id)

        
            user_liked = await sync_to_async(blog.likes.filter(id=user.id).exists)()
            if user_liked:
                await sync_to_async(blog.likes.remove)(user)
                message = 'Unliked successfully'
            else:
                await sync_to_async(blog.likes.add)(user)
                message = 'Liked successfully'

            return Response({"message":message},status=status.HTTP_200_OK) 
        except Blogs.DoesNotExist:
            return Response({'Blog Not found'},status=status.HTTP_404_NOT_FOUND)    



class Comment_Create_View(APIView):
    permission_classes =[IsAuthenticated]
    @swagger_auto_schema(
            request_body=CommentSerializer,
            responses = {200: CommentSerializer}
    )
    async def post(self, request,blog_id):
        try:
            blog =await Blogs.objects.aget(id=blog_id)
        except Blogs.DoesNotExist:
            return Response("Blog not found", status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer( data = request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        saved_coment = await sync_to_async(serializer.save)(user= request.user, blog=blog)

        comment_data = await Comment.objects.select_related('user','blog','blog__user').aget(id=saved_coment.id)

        data = await sync_to_async(lambda: CommentSerializer(comment_data).data)()
        return Response({"Commented successfully":data},status=status.HTTP_201_CREATED)
    


class Comment_Get_view(APIView):    
    async def get(self,request,id):
        try:
            comment = await Comment.objects.select_related('user','blog__user').aget(id=id)
            data =  CommentSerializer(comment).data
            return Response({'data':data},status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response("comment does not found", status=status.HTTP_404_NOT_FOUND)
           
    
class GetAllUserCommentsView(APIView):
    async def get(self,request):
        try:
            user = await sync_to_async(list)(Comment.objects.select_related('user').filter(user=request.user))
        except Comment.DoesNotExist:
            return Response("User comments not found", status=status.HTTP_404_NOT_FOUND)

        paginator = PageNumberPagination()
        paginator.page_size = 3
        result = await sync_to_async(paginator.paginate_queryset)(user, request)

        data = await sync_to_async(lambda: CommentSerializer(result, many = True).data)()

        return Response(paginator.get_paginated_response(data).data,status=status.HTTP_200_OK)   
    
        
class Comment_Put_view(APIView):
    permission_classes = [IsAuthenticated,IsOwnerOfBlog]
    @swagger_auto_schema(
            request_body=CommentSerializer,
            responses = {200: CommentSerializer}
    )
    async def put(self, request,id):
        try:
            comment = await Comment.objects.aget(id=id)
            await sync_to_async(self.check_object_permissions)(request,comment)
            serializer = CommentSerializer(comment, data=request.data)
        
            await sync_to_async(serializer.is_valid)(raise_exception=True)
            await sync_to_async(serializer.save)()
            updated_comment = await Comment.objects.select_related('user').aget(id=id)
            data = await sync_to_async(lambda: CommentSerializer(updated_comment).data)()
            return Response({'updated successfully':data},status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response("comment does not found", status=status.HTTP_404_NOT_FOUND) 

class Comment_Delete_view(APIView):  
    permission_classes = [IsAuthenticated]
    async def delete(self,request,id):
      try:  
        comment= await Comment.objects.aget(id=id)
        data =await  sync_to_async(lambda: CommentSerializer(comment).data)()
        await comment.adelete()

        return Response({'the comment is deleted':data},status=status.HTTP_200_OK)
      except Comment.DoesNotExist:
            return Response("comment does not found", status=status.HTTP_404_NOT_FOUND)
      

class User_Follow_View(APIView):
    permission_classes = [IsAuthenticated]

    async def post(self,request,user_id):
        serializer = await sync_to_async(FollowSerializer)(data = request.data)
        await sync_to_async(serializer.is_valid)(raise_exception=True)
        user = request.user
        
        try:
            followed_user = await User.objects.aget(id = user_id)
            
        except User.DoesNotExist:
            return Response("User Not found",status=status.HTTP_404_NOT_FOUND)

        try: 
            follow_request = await Followers.objects.filter(user = request.user, followed_user = followed_user, status__in=['pending','accepted']).afirst()
            
            if follow_request:
                if follow_request.status == 'accepted':
                    return Response("you are already following this user", status=status.HTTP_400_BAD_REQUEST)
                if follow_request.status == 'pending':
                    return Response("your request is on pending ", status=status.HTTP_400_BAD_REQUEST)
            
            await Followers.objects.acreate(user =user, followed_user=followed_user,status = 'pending')
            message = "Follow request sent Successfully"

            return Response({"message":message},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)


class AcceptFollowView(APIView):
    permission_classes = [IsAuthenticated]
    async def post(self,request, follow_request_id):
        try:
            follow = await Followers.objects.select_related('user').aget(id = follow_request_id, followed_user =request.user, status='pending')
            follow.status = 'accepted'
            await follow.asave()
            return Response("Follow request accepted",status=status.HTTP_200_OK)
        except Followers.DoesNotExist:
            return Response("request Not found",status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)

class GetFollowPendingRequestView(APIView):
    permission_classes = [IsAuthenticated]
    async def get(self,request):
        try:
            follows = await sync_to_async(list)(Followers.objects.select_related('user').filter(followed_user =request.user, status='pending'))
            data =[ {
                'id': follow.id,
                'user':follow.user.first_name,
                'status':follow.status
            } for follow in follows]

            return Response({'data':data},status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)

class RejectFollowView(APIView):
    permission_classes = [IsAuthenticated]
    async def post(self,request,follow_request_id):
        try:
            follow = await Followers.objects.select_related('user').aget(id = follow_request_id, followed_user =request.user)
            if follow.status == 'accepted':
                return Response("You already accept its followed request, unfollow it for rejection", status=status.HTTP_400_BAD_REQUEST)
            follow.status = 'rejected'
            await follow.asave()

            return Response("Follow request rejected",status=status.HTTP_200_OK)
        except Followers.DoesNotExist:
            return Response("request Not found",status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)

            
class UnfollowView(APIView):
    permission_classes = [IsAuthenticated]
    async def delete(self, request, follow_record_id):
        try:

            follow = await Followers.objects.select_related('user').aget(id=follow_record_id, followed_user=request.user, status = 'accepted')
            if follow:
               await follow.adelete()
               return Response(f"unFollowed {follow.user.first_name}",status=status.HTTP_200_OK)
            else:
                return Response({"error": "You are not following this user or the follow request is not accepted."}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response("User Not found",status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)       

class GetFollowersView(APIView):
    async def get(self,request):
        try:
            follower = await sync_to_async(list)(Followers.objects.select_related('user').filter(followed_user = request.user,status='accepted'))

            followed_users = [f.user for f in follower]
            paginator = PageNumberPagination()
            paginator.page_size = 3
            result = await sync_to_async(paginator.paginate_queryset)(followed_users, request)

            data = await sync_to_async(lambda: UserProfileSerializer(result, many =True).data)()

            return Response(paginator.get_paginated_response(data).data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST) 

       
class FollowingView(APIView):
    async def get(self,request):
        try:
            following = await sync_to_async(list)(Followers.objects.select_related('followed_user').filter(user = request.user, status='accepted'))

            following_users = [f.followed_user for f in following]
            

            paginator = PageNumberPagination()
            paginator.page_size = 15
            result = await sync_to_async(paginator.paginate_queryset)(following_users,request)
            data = await sync_to_async(lambda: UserProfileSerializer(result, many = True).data)()

            return Response(paginator.get_paginated_response(data).data,status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST) 



class CreateStory(APIView):
    async def post(self, request):
        try:
            request.data['expire_at'] = timezone.now() + timezone.timedelta(hours=24)
            serializer =  StorySerializer(data = request.data)
            
            await sync_to_async(serializer.is_valid)(raise_exception=True)
            saved_data = await sync_to_async(serializer.save)(user= request.user)
            
            story_data = await Story.objects.select_related('user').prefetch_related('viewers').aget(id=saved_data.id)
            data = await sync_to_async(lambda: StorySerializer(story_data).data)()
            return Response({'Story created ':data},status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST) 
    
class GetStory(APIView):
    async def get(self, request):
        
        try:
            story = Story.objects.select_related('user').prefetch_related('viewers').filter(expire_at__gt = timezone.now(), is_expired =False).exclude(viewers = request.user)

            serializer =await  sync_to_async(lambda:StorySerializer(story, many = True).data)()

            return Response({'Stories':serializer}, status=status.HTTP_200_OK)
        except Story.DoesNotExist:
            return Response("Story not found or expired",status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST) 
        
class TrackViewers(APIView):
    async def post(self, request, story_id):
        try:
            story = await Story.objects.select_related('user').prefetch_related('viewers').aget(id =story_id, expire_at__gt=timezone.now())
            if not await sync_to_async(story.viewers.filter(id= request.user.id).exists)():    
                await story.viewers.aadd(request.user)
                await story.asave()
                return Response({"Message":"Views Is Tracked"}, status=status.HTTP_200_OK)

        except Story.DoesNotExist:
            return Response("Story not found or expired",status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST) 
        
class DeleteStory(APIView):
    async def delete(self, request, story_id):
        try:
            story = await Story.objects.aget(id=story_id, user = request.user)
            serializer =await sync_to_async(lambda: StorySerializer(story).data)()
            await story.adelete()
            return Response({"message":"Story is deleted","story":serializer}, status=status.HTTP_200_OK)
        except Story.DoesNotExist:
            return Response("Story not found",status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error":str(e)},status=status.HTTP_400_BAD_REQUEST)