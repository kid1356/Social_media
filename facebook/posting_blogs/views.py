from rest_framework import status
from rest_framework.permissions import IsAuthenticated,BasePermission
from rest_framework.response import Response
from adrf.views import APIView
from drf_yasg.utils import swagger_auto_schema
from .serializers import *
from .models import *
from rest_framework.pagination import PageNumberPagination
from user.serializers import UserProfileSerializer
from asgiref.sync import sync_to_async
from django.db import transaction

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

        return paginator.get_paginated_response(data)
        
    

        

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

        return paginator.get_paginated_response(data)   
    
        
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

    def post(self,request,id):
        serializer = FollowSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        
        try:
            followed_user = User.objects.get(id = id)
        except User.DoesNotExist:
            return Response("User Not found",status=status.HTTP_404_NOT_FOUND)
 
        follow_request = Followers.objects.filter(user = request.user, followed_user = followed_user).first()
        if follow_request:
                if follow_request.status == 'accepted':
                    return Response("you are already following this user", status=status.HTTP_400_BAD_REQUEST)
                if follow_request.status == 'pending':
                    return Response("your request is on pending ", status=status.HTTP_400_BAD_REQUEST)

        Followers.objects.create(user =user, followed_user=followed_user,status = 'pending')
        message = "Follow request sent Successfully"

        return Response({"message":message},status=status.HTTP_200_OK)


class AcceptFollowView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request, follow_request_id):
        try:
            follow = Followers.objects.get(id = follow_request_id, followed_user =request.user, status='pending')
            follow.status = 'accepted'
            follow.save()
            return Response("Follow request accepted",status=status.HTTP_200_OK)
        except Followers.DoesNotExist:
            return Response("request Not found",status=status.HTTP_404_NOT_FOUND)



class RejectFollowView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request,follow_request_id):
        try:
            follow = Followers.objects.get(id = follow_request_id, followed_user =request.user)
            if follow.status == 'accepted':
                return Response("You already accept its followed request, unfollow it for rejection", status=status.HTTP_400_BAD_REQUEST)
            follow.status = 'rejected'
            follow.save()

            return Response("Follow request rejected",status=status.HTTP_200_OK)
        except Followers.DoesNotExist:
            return Response("request Not found",status=status.HTTP_404_NOT_FOUND)

            
class UnfollowView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, id):
        try:
            user =  User.objects.get(id=id)

            follow = Followers.objects.filter(user = request.user, followed_user=user, status = 'accepted')
            if follow.exists():
               follow.delete()
               return Response(f"unFollowed {user.first_name}",status=status.HTTP_200_OK)
            else:
                return Response({"error": "You are not following this user or the follow request is not accepted."}, status=status.HTTP_400_BAD_REQUEST)

        except User.DoesNotExist:
            return Response("User Not found",status=status.HTTP_404_NOT_FOUND)


class GetFollowersView(APIView):
    def get(self,request):
        user = request.user
        follower = Followers.objects.filter(followed_user = user)

        followed_users = [f.user for f in follower]
        paginator = PageNumberPagination()
        paginator.page_size = 15
        result = paginator.paginate_queryset(followed_users, request)

        serializer = UserProfileSerializer(result, many =True)

        return Response(paginator.get_paginated_response(serializer.data).data,status=status.HTTP_200_OK)

       
class FollowingView(APIView):
    def get(self,request):
        user = request.user
        following = Followers.objects.filter(user = user)

        following_users = [f.followed_user for f in following]
        

        paginator = PageNumberPagination()
        paginator.page_size = 15
        result =paginator.paginate_queryset(following_users,request)
        serializer = UserProfileSerializer(result, many = True)

        return Response(paginator.get_paginated_response(serializer.data).data,status=status.HTTP_200_OK)



class CreateStory(APIView):
    def post(self, request):
        
        user =request.user
        request.data['expire_at'] = timezone.now() + timezone.timedelta(hours=24)
        serializer =  StorySerializer(data = request.data)
        
        serializer.is_valid(raise_exception=True)
        serializer.save(user= user)

        return Response({'Story created ':serializer.data},status=status.HTTP_201_CREATED)
    
class GetStory(APIView):
    def get(self, request):
        user =request.user
        try:
            story = Story.objects.filter(expire_at__gt = timezone.now(), is_expired =False).exclude(viewers = user)

            serializer = StorySerializer(story, many = True)

            return Response({'Stories':serializer.data}, status=status.HTTP_200_OK)
        except Story.DoesNotExist:
            return Response("Story not found or expired",status=status.HTTP_404_NOT_FOUND)
    

class TrackViewers(APIView):
    def post(self, request, story_id):
        try:
            story = Story.objects.get(id =story_id, expire_at__gt=timezone.now())
            if not story.viewers.filter(id= request.user.id).exists():    
                story.viewers.add(request.user)
                story.save()
                return Response({"Message":"Views Is Tracked"}, status=status.HTTP_200_OK)

        except Story.DoesNotExist:
            return Response("Story not found or expired",status=status.HTTP_404_NOT_FOUND)
        
class DeleteStory(APIView):
    def delete(self, request, story_id):
        try:
            story = Story.objects.get(id=story_id, user = request.user)
            serializer =StorySerializer(story)
            story.delete()
            return Response({"message":"Story is deleted","story":serializer.data}, status=status.HTTP_200_OK)
        except Story.DoesNotExist:
            return Response("Story not found",status=status.HTTP_404_NOT_FOUND)