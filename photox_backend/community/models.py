from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.core.exceptions import ValidationError

# 定义选择项
LIKE_TYPE_CHOICES = [
    ('album', '相册'),
    ('comment', '评论'),
    ('image', '图片'),
]

NOTIFICATION_TYPE_CHOICES = [
    ('like', '点赞'),
    ('comment', '评论'),
    ('follow', '关注'),
    ('system', '系统通知'),
]

class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    album = models.ForeignKey('albums.Album', on_delete=models.CASCADE, verbose_name="相册", null=True, blank=True)
    image = models.ForeignKey('images.Image', on_delete=models.CASCADE, verbose_name="图片", null=True, blank=True)
    content = models.TextField(verbose_name="评论内容")
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name="父评论")
    is_deleted = models.BooleanField(default=False, verbose_name="是否删除")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")

    class Meta:
        verbose_name = "评论"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def clean(self):
        # 允许album和image都为空，但不能同时设置两者
        if self.album and self.image:
            raise ValidationError('评论不能同时关联到相册和图片')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}: {self.content[:50]}"

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="用户")
    like_type = models.CharField(max_length=20, choices=LIKE_TYPE_CHOICES, verbose_name="点赞类型")
    object_id = models.PositiveIntegerField(default=0, verbose_name="对象ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        unique_together = ['user', 'like_type', 'object_id']
        verbose_name = "点赞"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.user.username} 点赞了 {self.like_type}:{self.object_id}"

class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='following', verbose_name="关注者")
    following = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='followers', verbose_name="被关注者")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="关注时间")

    class Meta:
        unique_together = ['follower', 'following']
        verbose_name = "关注关系"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.follower.username} 关注了 {self.following.username}"

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications', verbose_name="接收用户")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_notifications', null=True, blank=True, verbose_name="发送用户")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPE_CHOICES, verbose_name="通知类型")
    content = models.TextField(verbose_name="通知内容")
    is_read = models.BooleanField(default=False, verbose_name="是否已读")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        verbose_name = "通知"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return f"通知给 {self.user.username}: {self.content[:50]}"

class Favorite(models.Model):
    """收藏模型"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites', verbose_name="用户")
    image = models.ForeignKey('images.Image', on_delete=models.CASCADE, related_name='favorited_by', verbose_name="图片")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="收藏时间")

    class Meta:
        verbose_name = "收藏"
        verbose_name_plural = verbose_name
        unique_together = [['user', 'image']]  # 确保用户不能重复收藏同一张图片
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} 收藏了 {self.image.title}"