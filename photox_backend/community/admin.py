from django.contrib import admin
from .models import Comment, Like, Follow, Notification

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'album', 'content', 'parent', 'created_at']
    list_filter = ['created_at', 'is_deleted']
    search_fields = ['user__username', 'content']
    raw_id_fields = ['user', 'album', 'parent']

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'like_type', 'object_id', 'created_at']
    list_filter = ['like_type', 'created_at']
    search_fields = ['user__username']
    raw_id_fields = ['user']

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ['id', 'follower', 'following', 'created_at']
    list_filter = ['created_at']
    search_fields = ['follower__username', 'following__username']
    raw_id_fields = ['follower', 'following']

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'sender', 'notification_type', 'content', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'sender__username', 'content']
    raw_id_fields = ['user', 'sender']