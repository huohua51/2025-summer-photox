from rest_framework import serializers
from .models import Album

class AlbumSerializer(serializers.ModelSerializer):
    # 使用字符串方式引用，避免循环导入
    images = serializers.SerializerMethodField()
    user = serializers.ReadOnlyField(source='user.username')
    image_count = serializers.SerializerMethodField()

    class Meta:
        model = Album
        fields = ['id', 'title', 'description', 'user', 'images', 'image_count', 'is_public', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_images(self, obj):
        # 懒加载图片序列化器，避免循环导入
        from images.serializers import ImageSerializer
        return ImageSerializer(obj.images.all(), many=True, context=self.context).data
    
    def get_image_count(self, obj):
        return obj.images.count()

class AlbumCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['title', 'description', 'is_public']

class AlbumUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Album
        fields = ['title', 'description', 'is_public'] 