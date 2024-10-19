from django.shortcuts import render
from user.views import *
from .serializers import *
from .models import *
from rest_framework.pagination import PageNumberPagination
from user.serializers import UserProfileSerializer


#custom permissions
class IsOwnerOfBlog(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET', 'HEAD', 'OPTIONS']:  # Can read the object only
            return True

        return obj.user == request.user
        

# Create your views here.  
class Blog_Create_view(APIView):
    def post(self, request):
        serializer = BlogSerializer(data= request.data)         #posting Blogs 
        serializer.is_valid(raise_exception=True)
        serializer.save(user = request.user)

        return Response({'The Blogs is Posted':serializer.data},status=status.HTTP_201_CREATED)



#Getting all blogs or post from a specific User
class GetAllUserBlogsView(APIView):
    def get(self,request,user_id):
        try:                                                                
            user = Blogs.objects.filter(user_id=user_id)
        except User.DoesNotExist:
            return Response("User blogs not found",status=status.HTTP_404_NOT_FOUND)
        paginator = PageNumberPagination()
        paginator.page_size = 15
        result = paginator.paginate_queryset(user, request)

        serializer = BlogSerializer(result,many = True)

        return paginator.get_paginated_response(serializer.data)

        

# getting single blogs by id
class Blog_Get_view(APIView):
        
    def get(self,request,id):
        try:
            blog = Blogs.objects.get(id=id)
            serializer = BlogSerializer(blog)
            return Response({'Blog':serializer.data},status=status.HTTP_200_OK)
        except Blogs.DoesNotExist:
            return Response({"Blog not Found"},status=status.HTTP_404_NOT_FOUND)


# Updating blog 
class Blog_Patch_view(APIView):   
    permission_classes = [IsOwnerOfBlog]
    def patch(self, request,id):
        try:
            blog = Blogs.objects.get(id=id)

            self.check_object_permissions(request,blog)

            serializer = BlogSerializer(blog, data=request.data, partial = True)
        
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'updated successfully':serializer.data},status=status.HTTP_200_OK)
        except Blogs.DoesNotExist:
            return Response('Blog Does not FOund',status=status.HTTP_404_NOT_FOUND)


#Deleting blog
class DeleteBlogView(APIView):
    permission_classes = [IsOwnerOfBlog]
    def delete(self, request,id):
        try:
            blog = Blogs.objects.get(id=id)
            serializer = BlogSerializer(blog)
            blog_serialized = serializer.data
            self.check_object_permissions(request, blog)
            blog.delete()
            return Response({"the blog is deleted":blog_serialized}, status=status.HTTP_200_OK)

        except Blogs.DoesNotExist:
            return Response({"blog DOes not found or already deleted"}, status=status.HTTP_400_BAD_REQUEST)




# liking A blog
class Like_Blog_view(APIView):
    def post(self,request,id):
        user = request.user

        try:
            blog = Blogs.objects.get(id=id)
        except Blogs.DoesNotExist:
            return Response({'Blog Not found'},status=status.HTTP_404_NOT_FOUND)

        if user in blog.likes.all():
            blog.likes.remove(user)
            message = 'Unliked successfully'
        else:
            blog.likes.add(user)
            message = 'Liked successfully'

        return Response({"message":message},status=status.HTTP_200_OK)     



class Comment_Create_View(APIView):
   
    def post(self, request,blog_id):
        try:
            blog = Blogs.objects.get(id=blog_id)
        except Blogs.DoesNotExist:
            return Response("Blog not found", status=status.HTTP_404_NOT_FOUND)
        serializer = CommentSerializer( data = request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user= request.user, blog=blog)

        return Response({"Commented successfully":serializer.data},status=status.HTTP_201_CREATED)
    


class Comment_Get_view(APIView):    
    def get(self,request,id):
        try:
            comment = Comment.objects.get(id=id)
            serializer = CommentSerializer(comment)
            return Response({'Comment':serializer.data},status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response("comment does not found", status=status.HTTP_404_NOT_FOUND)
        
class GetAllUserCommentsView(APIView):
    def get(self,request,user_id):
        try:
            user = Comment.objects.filter(user_id=user_id)
        except Comment.DoesNotExist:
            return Response("User comments not found", status=status.HTTP_404_NOT_FOUND)

        paginator = PageNumberPagination()
        paginator.page_size = 15
        result = paginator.paginate_queryset(user, request)

        serializer = CommentSerializer(result, many = True)

        return paginator.get_paginated_response(serializer.data)     

    
        
class Comment_Put_view(APIView):
    permission_classes = [IsOwnerOfBlog]
    def put(self, request,id):
        try:
            comment = Comment.objects.get(id=id)
            self.check_object_permissions(request,comment)
            serializer = CommentSerializer(comment, data=request.data)
        
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({'updated successfully':serializer.data},status=status.HTTP_200_OK)
        except Comment.DoesNotExist:
            return Response("comment does not found", status=status.HTTP_404_NOT_FOUND)

class Comment_Delete_view(APIView):  
    def delete(self,request,id):
      try:  
        comment= Comment.objects.get(id=id)
        serializer = CommentSerializer(comment)
        serializer_data = serializer
        comment.delete()

        return Response({'the comment is deleted':serializer_data},status=status.HTTP_200_OK)
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

