from django.urls import path
from .views import Blog_Create_view,Blog_Get_view,Blog_Patch_view,GetAllUserBlogsView,DeleteBlogView,Comment_Create_View,GetAllUserCommentsView,Comment_Get_view,Comment_Delete_view,Comment_Put_view,Like_Blog_view,User_Follow_View,GetFollowersView,GetFollowPendingRequestView,AcceptFollowView,RejectFollowView,UnfollowView,FollowingView,CreateStory,GetStory,TrackViewers,DeleteStory

urlpatterns = [
    path('create-blog/',Blog_Create_view.as_view(),name= 'create-blog-view'),
    path('get-blog/<int:id>/',Blog_Get_view.as_view(),name= 'get-blog-view'),
    path('user/get-all-blogs',GetAllUserBlogsView.as_view(),name= 'get-all-user-blog-view'),
    path('edit-blog/<int:id>/',Blog_Patch_view.as_view(),name= 'put-blog-view'),
    path('delete-blog/<int:id>/',DeleteBlogView.as_view(),name =' Delete-view'),
    path('comment-blog/<int:blog_id>/',Comment_Create_View.as_view(),name= 'create-comment-view'),
    path('user/get-all-comments/',GetAllUserCommentsView.as_view(),name= 'get-all-user-comments-view'),
    path('get-comment-of-blog/<int:id>/',Comment_Get_view.as_view(),name= 'get-comment-view'),
    path('edit-comment/<int:id>/',Comment_Put_view.as_view(),name= 'put-comment-view'),
    path('delete-comment/<int:id>/',Comment_Delete_view.as_view(),name =' Delete-comment-view'),
    path('like-blog/<int:id>/',Like_Blog_view.as_view(),name =' Like-view'),
    path('follow/<int:user_id>/',User_Follow_View.as_view(),name =' followView'),
    path('get-pending-follow-requests/',GetFollowPendingRequestView.as_view(), name ="pendingrequests" ),
    path('accept-follow-request/<int:follow_request_id>/',AcceptFollowView.as_view(),name =' acceptfollowView'),
    path('reject-follow-request/<int:follow_request_id>/',RejectFollowView.as_view(),name =' rejectfollowView'),
    path('unfollow/<int:follow_record_id>/',UnfollowView.as_view(),name =' unfollowView'),
    path('get-follower/',GetFollowersView.as_view(),name =' getfollowerView'),
    path("following/",FollowingView.as_view(),name='following'),
    path("story/",CreateStory.as_view(),name='createstory'),
    path("get-stories/view/",GetStory.as_view(),name='getstory'),
    path('stories/<int:story_id>/views/',TrackViewers.as_view(), name='viewers'),
    path("stories/<int:story_id>/delete/",DeleteStory.as_view(),name='deletestories'),
]   