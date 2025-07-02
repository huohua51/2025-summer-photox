import logging
import json
import ast
from rest_framework import serializers
from .models import Image
from community.models import Like, Follow
from users.serializers import UserSerializer

# 初始化日志记录器
logger = logging.getLogger(__name__)


def safe_load_tags(tags_data):
    """
    安全地将可能为字符串或多次编码的 JSON 数据转换成列表。
    处理多种格式：
      - 正常 list
      - JSON str (单层/双层编码)
      - ast.literal_eval 格式
    """
    if isinstance(tags_data, list):
        return tags_data

    if not isinstance(tags_data, str):
        return []

    # Step 1: 尝试使用 ast.literal_eval 解析（适用于简单列表）
    try:
        parsed = ast.literal_eval(tags_data)
        if isinstance(parsed, list):
            return parsed
    except (ValueError, SyntaxError):
        pass

    # Step 2: 尝试直接解析原始字符串为 list
    try:
        parsed = json.loads(tags_data)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass

    # Step 3: 如果仍然失败，可能是嵌套了多层 json.dumps()
    try:
        decoded_once = json.loads(tags_data)
        if isinstance(decoded_once, str):
            decoded_twice = json.loads(decoded_once)
            if isinstance(decoded_twice, list):
                return decoded_twice
        else:
            return decoded_once
    except json.JSONDecodeError:
        pass

    # Step 4: 所有解析都失败，返回空列表
    logger.warning(f"无法解析 tags 字段: {tags_data}")
    return []


class ImageSerializer(serializers.ModelSerializer):
    """序列化Image模型"""
    tags_list = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField() 
    like_count = serializers.SerializerMethodField()
    user = UserSerializer(read_only=True)  # 使用UserSerializer序列化用户信息
    is_following_author = serializers.SerializerMethodField()  # 添加关注状态字段
    is_liked = serializers.SerializerMethodField()  # 添加当前用户是否点赞

    class Meta:
        model = Image
        fields = [
            'id', 'image_url', 'title', 'tags', 'tags_list',
            'user', 'created_at', 'is_public',
            'category_id', 'category', 'colors', 'like_count', 
            'is_following_author', 'is_liked'
        ]
    
    def get_tags_list(self, obj):
        """获取标签列表"""
        return obj.get_tags_as_list()
    
    def get_like_count(self, obj):
        """获取图片点赞数量"""
        return Like.objects.filter(like_type='image', object_id=obj.id).count()
    
    def get_is_following_author(self, obj):
        """获取当前用户是否关注图片作者"""
        request = self.context.get('request')
        if request and request.user.is_authenticated and obj.user:
            # 检查当前用户是否关注图片作者
            return Follow.objects.filter(
                follower=request.user, 
                following=obj.user
            ).exists()
        return False

    def get_is_liked(self, obj):
        """获取当前用户是否已点赞该图片"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Like.objects.filter(
                user=request.user,
                like_type='image',
                object_id=obj.id
            ).exists()
        return False

    def to_representation(self, instance):
        data = super().to_representation(instance)

        # 获取原始 tags 字段
        raw_tags = instance.tags

        # 安全解析标签
        parsed_tags = safe_load_tags(raw_tags)

        # 替换原来的 tags 字段
        data['tags'] = parsed_tags

        # 确保用户头像URL正确
        if data.get('user') and data['user'].get('avatar'):
            avatar_url = data['user']['avatar']
            # 如果头像URL不是完整URL，添加域名前缀
            if avatar_url and not avatar_url.startswith('http'):
                from django.conf import settings
                if hasattr(settings, 'QINIU_DOMAIN'):
                    data['user']['avatar'] = f"{settings.QINIU_DOMAIN}/{avatar_url}"
                else:
                    # 使用默认域名或当前请求的域名
                    request = self.context.get('request')
                    if request:
                        data['user']['avatar'] = request.build_absolute_uri(avatar_url)

        return data

    def get_category(self, obj):
        # category_map = {
        #     0: "其他", 1: "风景", 2: "人物肖像", 3: "动物", 4: "食品",
        #     5: "建筑", 6: "电子产品", 7: "植物花卉", 8: "家具家居",
        #     9: "服装鞋帽", 10: "艺术创作", 11: "运动器材", 12: "交通工具"
        # }
        category_map = {
            0: "其他", 1: "风景", 2: "人物肖像", 3: "动物", 4: "食品",
            5: "建筑", 6: "电子产品", 7: "植物花卉", 8: "家具家居", 9: "服装鞋帽",
            10: "艺术创作", 11: "运动器材", 12: "交通工具", 13: "宠物用品", 14: "美妆用品"
        }
        return category_map.get(obj.category_id, "未知")


class ImageUploadSerializer(serializers.Serializer):
    """处理图片上传请求"""
    image = serializers.ImageField()
    title = serializers.CharField(required=False, max_length=255)
    is_public = serializers.BooleanField(required=False, default=False)