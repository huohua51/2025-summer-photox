# community/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Comment, Like, Follow, Notification
from albums.models import Album

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """用户序列化器"""
    is_following = serializers.SerializerMethodField()
    follower_count = serializers.SerializerMethodField()
    following_count = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_joined', 'is_following', 'follower_count', 'following_count']
        ref_name = 'CommunityUser'
        
    def get_is_following(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Follow.objects.filter(follower=request.user, following=obj).exists()
        return False
    
    def get_follower_count(self, obj):
        return obj.followers.count()
    
    def get_following_count(self, obj):
        return obj.following.count()


class CommentSerializer(serializers.ModelSerializer):
    """评论序列化器"""
    user = UserSerializer(read_only=True)
    reply_count = serializers.ReadOnlyField()
    like_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'album', 'image', 'content', 'parent', 'created_at', 'updated_at', 
                 'reply_count', 'like_count', 'is_liked', 'replies']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate(self, data):
        """验证数据"""
        album = data.get('album')
        image = data.get('image')
        
        # 允许album和image都为空，但不能同时设置两者
        if album and image:
            raise serializers.ValidationError('评论不能同时关联到相册和图片')
        
        return data
        
    def get_like_count(self, obj):
        """获取评论点赞数量"""
        return Like.objects.filter(like_type='comment', object_id=obj.id).count()
        
    def get_is_liked(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user, 
                like_type='comment', 
                object_id=obj.id
            ).exists()
        return False
    
    def get_replies(self, obj):
        if obj.parent is None:  # 只有顶级评论才显示回复
            replies = obj.replies.filter(is_deleted=False)[:3]  # 默认显示前3条回复
            return CommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def create(self, validated_data):
        comment = Comment.objects.create(**validated_data)
        
        # 创建通知
        if comment.parent:
            # 回复评论通知（允许回复自己）
            Notification.objects.create(
                user=comment.parent.user,
                sender=comment.user,
                notification_type='reply',
                content=f'{comment.user.username} 回复了你的评论'
            )
        else:
            # 评论通知
            if comment.image and comment.image.user != comment.user:
                # 评论图片通知
                Notification.objects.create(
                    user=comment.image.user,
                    sender=comment.user,
                    notification_type='comment',
                    content=f'{comment.user.username} 评论了你的图片'
                )
            elif comment.album and comment.album.user != comment.user:
                # 评论相册通知
                Notification.objects.create(
                    user=comment.album.user,
                    sender=comment.user,
                    notification_type='comment',
                    content=f'{comment.user.username} 评论了你的相册'
                )
        
        return comment


class LikeSerializer(serializers.ModelSerializer):
    """点赞序列化器"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'like_type', 'object_id', 'created_at']
        read_only_fields = ['created_at']
    
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        like_type = validated_data['like_type']
        object_id = validated_data['object_id']
        # 检查对象是否存在
        if like_type == 'album':
            if not Album.objects.filter(id=object_id).exists():
                raise serializers.ValidationError('相册不存在')
        elif like_type == 'comment':
            if not Comment.objects.filter(id=object_id).exists():
                raise serializers.ValidationError('评论不存在')
        elif like_type == 'image':
            from images.models import Image
            if not Image.objects.filter(id=object_id).exists():
                raise serializers.ValidationError('图片不存在')
        return Like.objects.create(**validated_data)


class FollowSerializer(serializers.ModelSerializer):
    """关注序列化器"""
    follower = UserSerializer(read_only=True)
    following = UserSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """通知序列化器"""
    sender = UserSerializer(read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'sender', 'notification_type', 'content', 'is_read', 'created_at']
        read_only_fields = ['created_at']


class AlbumWithStatsSerializer(serializers.ModelSerializer):
    """带统计信息的相册序列化器"""
    user = UserSerializer(read_only=True)
    comment_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Album
        fields = ['id', 'title', 'description', 'user', 'created_at', 'comment_count']
    
    def get_comment_count(self, obj):
        return obj.comment_set.filter(is_deleted=False).count()