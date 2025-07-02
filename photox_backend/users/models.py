from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('user', '普通用户'),
        ('admin', '管理员'),
        ('moderator', '版主'),
    ]
    
    nickname = models.CharField(max_length=50, blank=True, null=True, verbose_name="昵称")
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="头像")
    bio = models.TextField(max_length=500, blank=True, null=True, verbose_name="简介")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user', verbose_name="角色")
    is_verified = models.BooleanField(default=False, verbose_name="是否验证")
    
    # 为时间字段提供默认值
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    
    can_manage_users = models.BooleanField(default=False, verbose_name="用户管理权限")
    can_manage_tags = models.BooleanField(default=False, verbose_name="标签管理权限")
    can_manage_templates = models.BooleanField(default=False, verbose_name="模型管理权限")
    can_view_statistics = models.BooleanField(default=False, verbose_name="数据查看权限")

    def __str__(self):
        return self.nickname if self.nickname else self.username
    
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser
    
    def is_moderator(self):
        return self.role in ['admin', 'moderator'] or self.is_superuser

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name