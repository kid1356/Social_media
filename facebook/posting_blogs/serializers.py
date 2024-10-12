from user.serializers import *
from .models import *

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    blog_info = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = ['user','text','blog_info']
        extra_kwargs = {
            'text':{'required':True}
        }

    def get_user(self,obj):
        return obj.user.first_name
    
    def get_blog_info(self,obj):
        blog = obj.blog
        blog_image = getattr(blog, 'images', None)
        blog_file = getattr(blog, 'file', None)
        return{
            'blog_file':blog_file.url if blog_file else None,
            'blog_image':blog_image.url if blog_image else None,
            'blog_text' :blog.text,
            'blog_owner': blog.user.first_name
        }



class BlogSerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    likers = serializers.SerializerMethodField()

    class Meta:
        model = Blogs
        fields = ['user','text','images','file','total_likes','likers']
        extra_kwargs = {
            'text':{'required':True}
        }
        
    def get_user(self,obj):
        return obj.user.first_name

    def get_total_likes(self,obj):
        return obj.likes.count()
    
    def get_likers(self,obj):
        return UserProfileSerializer(obj.likes.all(),many =True).data


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Followers
        fields = ['user','created_at']

        extra_kwargs = {
            'user':{'read_only':True}
        }