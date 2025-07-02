from rest_framework import serializers
from tags.models import Tag

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['id', 'name']  # 只包含ID和名称
        read_only_fields = ('id',)  # 移除时间字段引用

class TagImportSerializer(serializers.Serializer):
    file = serializers.FileField(help_text="包含标签数据的文本文件")