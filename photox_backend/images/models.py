from django.db import models

# Create your models here.
# images/models.py
from django.db import models
# 确保从 users app 导入 CustomUser
# from users.models import CustomUser
# 或者使用 settings.AUTH_USER_MODEL 避免循环导入
from django.conf import settings


class Image(models.Model):
    title = models.CharField(max_length=255, blank=True, verbose_name="标题")
    # image_url 存储在云存储的地址
    image_url = models.URLField(max_length=1024, verbose_name="图片URL")
    # 使用 settings.AUTH_USER_MODEL 指向 CustomUser 模型
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='images', on_delete=models.CASCADE, verbose_name="所属用户")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    # AI 分析生成的标签，存储为JSON字符串
    tags = models.TextField(blank=True, null=True, verbose_name="AI标签")
    is_public = models.BooleanField(default=False)  # 个人图片默认私有
    colors = models.JSONField(default=list)  # 默认空
    category_id = models.IntegerField(null=True, blank=True, verbose_name="种类ID")
    ai_description = models.TextField(blank=True, null=True, verbose_name="AI智能分析")
    ai_style_analysis = models.JSONField(default=dict, blank=True, verbose_name="AI风格分析")
    ai_emotion_analysis = models.JSONField(default=dict, blank=True, verbose_name="AI情感分析")
    user_tags = models.JSONField(default=list, blank=True, verbose_name="用户自定义标签")

    def __str__(self):
        return self.title or f"Image {self.id}"

    def get_tags_as_list(self):
        """将标签字符串转换为列表"""
        if not self.tags:
            return []
        if isinstance(self.tags, list):
            return self.tags
        try:
            # 首先尝试使用 ast.literal_eval（适用于简单列表）
            import ast
            return ast.literal_eval(self.tags)
        except (ValueError, SyntaxError):
            try:
                # 尝试解析JSON
                import json
                return json.loads(self.tags)
            except:
                # 如果解析失败，按逗号分隔
                return [tag.strip() for tag in self.tags.split(',')]

    class Meta:
        verbose_name = "图片"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']
