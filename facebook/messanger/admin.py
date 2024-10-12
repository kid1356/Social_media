from django.contrib import admin
from .models import *
from django.utils.safestring import mark_safe
# Register your models here.
@admin.register(Messages)
class  messages(admin.ModelAdmin):
    list_display = ['id','sender','receiver','text','room','file']



@admin.register(Room)
class room(admin.ModelAdmin):
    list_display = ['id','name','room_type']


@admin.register(MessageReadStatus)
class readstatus(admin.ModelAdmin):
    list_display = ['id','user','message','is_read','read_at']