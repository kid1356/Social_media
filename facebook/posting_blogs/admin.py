from django.contrib import admin
from .models import *
# Register your models here.
@admin.register(Comment)
class CommentBlog(admin.ModelAdmin):
    list_display = ['id','user','text','blog_text','blog_owner','created_at']
    search_fields = ['user']
    list_filter = ['created_at']

    fieldsets = (
        ('Comments', {'fields':('user','text','blog')}),
    )

    readonly_fields = ['blog_text','blog_owner']

    def blog_text(self,obj):
        return obj.blog.text
    
    blog_text.short_description = 'Blog Text'

    def blog_owner(self,obj):
        return obj.blog.user.first_name
    
    blog_owner.short_description = 'Blog Owner'

@admin.register(Blogs)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['id','user', 'text','images','file' ,'get_likes_count','created_at']
    search_fields = ['user']
    list_filter = ['created_at']
    

    fieldsets = (
        ('Blogs', {'fields':('user','text','images','file','get_likes_count')}),
    )
    readonly_fields = ['get_likes_count']


    def get_likes_count(self, obj):
        return obj.likes.count()

    get_likes_count.short_description = 'Likes Count'

@admin.register(Notification)
class notify(admin.ModelAdmin):
    list_display = ['id','user','message','is_read','timestamp']
    search_fields = ['user','is_read']


@admin.register(Followers)
class followers(admin.ModelAdmin):
    list_display = ['id','user','followed_user','followers_counts','created_at']
    search_fields = ['user']
    ordering = ['followed_user']

    def followers_counts(self,obj):
        return Followers.objects.filter(followed_user = obj.followed_user, status = 'accepted').count()
    
    followers_counts.short_description = 'Followers Count'


@admin.register(Story)
class story(admin.ModelAdmin):
    list_display = ['id','user','media','caption','visibilty','viewers_count','expire_at','created_at']
    search_fields = ['user']


    def viewers_count(self, obj):
        return obj.viewers.count()
    
    viewers_count.short_description = 'Viewers Count'