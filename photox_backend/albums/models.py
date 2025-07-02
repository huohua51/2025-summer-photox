"""
相册管理模块 - 数据模型
作者: x1x8j (1101219195@qq.com)
功能: 提供用户相册的创建、管理和分享功能
"""
from django.db import models
from django.conf import settings
# 从 images app 导入 Image 模型
from images.models import Image

class Album(models.Model):
    """
    相册模型
    用于管理用户创建的相册，支持将多张图片组织到一个相册中
    """
    title = models.CharField(max_length=255, verbose_name="相册标题")
    description = models.TextField(blank=True, null=True, verbose_name="描述")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='albums', on_delete=models.CASCADE, verbose_name="所属用户")
    # 使用 ManyToManyField 将图片关联到相册
    images = models.ManyToManyField(Image, related_name='albums', blank=True, verbose_name="包含图片")
    is_public = models.BooleanField(default=False, verbose_name="是否公开")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "相册"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']