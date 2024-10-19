from django.urls import path
from .views import *

urlpatterns = [
    path('create-blog/',Blog_Create_view.as_view(),name= 'create-blog-view'),
    path('get-blog/<int:id>/',Blog_Get_view.as_view(),name= 'get-blog-view'),
    path('user/get-all-blogs/<int:user_id>/',GetAllUserBlogsView.as_view(),name= 'get-all-user-blog-view'),
    path('edit-blog/<int:id>/',Blog_Patch_view.as_view(),name= 'put-blog-view'),
    path('delete-blog/<int:id>/',DeleteBlogView.as_view(),name =' Delete-view'),
    path('comment-blog/<int:blog_id>/',Comment_Create_View.as_view(),name= 'create-comment-view'),
    path('user/get-all-comments/<int:user_id>/',GetAllUserCommentsView.as_view(),name= 'get-all-user-comments-view'),
    path('get-comment-of-blog/<int:id>/',Comment_Get_view.as_view(),name= 'get-comment-view'),
    path('edit-comment/<int:id>/',Comment_Put_view.as_view(),name= 'put-comment-view'),
    path('delete-comment/<int:id>/',Comment_Delete_view.as_view(),name =' Delete-comment-view'),
    path('like-blog/<int:id>/',Like_Blog_view.as_view(),name =' Like-view'),
    path('follow/<int:id>/',User_Follow_View.as_view(),name =' followView'),
    path('accept-follow-request/<int:follow_request_id>/',AcceptFollowView.as_view(),name =' acceptfollowView'),
    path('reject-follow-request/<int:follow_request_id>/',RejectFollowView.as_view(),name =' rejectfollowView'),
    path('unfollow/<int:id>/',UnfollowView.as_view(),name =' unfollowView'),
    
    path('get-follower/',GetFollowersView.as_view(),name =' getfollowerView'),
    path("following/",FollowingView.as_view(),name='following')

]   