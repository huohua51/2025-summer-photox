# users/serializers.py
from rest_framework import serializers
# from django.contrib.auth import get_user_model
# 或者直接导入
from .models import CustomUser

# User = get_user_model() # 获取 settings.AUTH_USER_MODEL 指定的模型

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'}, label="确认密码")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password', 'password_confirm'] # 可以添加更多注册时允许用户填写的字段
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True}
        }

    def validate(self, attrs):
        # 校验两次密码是否一致
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "两次输入的密码不一致。"})
        return attrs

    def create(self, validated_data):
        try:
            # 创建用户实例，移除确认密码字段
            validated_data.pop('password_confirm')
            # 使用 create_user 方法来创建用户，会自动处理密码哈希
            user = CustomUser.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],
                is_active=True  # 确保新用户是激活状态
            )
            return user
        except Exception as e:
            raise serializers.ValidationError(f"创建用户失败: {str(e)}")

# (可选) 如果需要返回用户信息，可以定义一个 UserSerializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        # 选择你希望在API中暴露的用户字段
        fields = ['id', 'username', 'nickname', 'email', 'avatar', 'bio', 'date_joined']
        read_only_fields = ['id', 'date_joined'] # 只读字段
        ref_name = 'User'

# 添加修改密码的序列化器
class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        # 校验两次密码是否一致
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"new_password": "两次输入的新密码不一致。"})
        return attrs