from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Comment)
class CommentBlog(admin.ModelAdmin):
    list_display = ['id','user','text','created_at','blog_text','blog_owner']

    def blog_text(self,obj):
        return obj.blog.text
    
    blog_text.short_description = 'Blog Text'

    def blog_owner(self,obj):
        return obj.blog.user.first_name
    
    blog_owner.short_description = 'Blog Owner'

@admin.register(Blogs)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'text', 'get_likes_count']



    def get_likes_count(self, obj):
        return obj.likes.count()

    get_likes_count.short_description = 'Likes Count'

@admin.register(Notification)
class notify(admin.ModelAdmin):
    list_display = ['id','user','message','is_read']


@admin.register(Followers)
class followers(admin.ModelAdmin):
    list_display = ['id','user','followed_user','created_at']


@admin.register(Story)
class story(admin.ModelAdmin):
    list_display = ['id','user','media','caption','visibilty','viewers_count','expire_at','created_at']


    def viewers_count(self, obj):
        return obj.viewers.count()
    
    viewers_count.short_description = 'Viewers Count'