from django.shortcuts import render

# Create your views here.
# users/views.py
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer
# from django.contrib.auth import get_user_model
from .models import CustomUser

# User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    用户注册视图
    """
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,) # 允许任何人访问注册接口
    serializer_class = RegisterSerializer

    # 重写 create 方法来自定义成功响应 (可选)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        # 不在响应中返回用户信息或 token，只返回成功消息
        return Response({"code": 0, "message": "用户注册成功"}, status=status.HTTP_201_CREATED)


# Simple JWT 提供了登录视图，我们通常直接使用它，但如果你想自定义返回格式可以包装一下
from rest_framework_simplejwt.views import TokenObtainPairView
import traceback
import logging
import json

logger = logging.getLogger(__name__)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        try:
            logger.info("开始处理登录请求...")
            username = request.data.get('username', '')
            password = request.data.get('password', '')
            logger.info(f"用户 {username} 尝试登录")
            
            # 检查用户是否存在
            try:
                user = CustomUser.objects.get(username=username)
                logger.info(f"用户 {username} 存在，is_active={user.is_active}")
                if not user.is_active:
                    logger.warning(f"用户 {username} 账号未激活")
                    return Response({
                        "code": 1,
                        "message": "账号未激活，请联系管理员",
                        "error": "Account is not active"
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
                # 验证密码
                if not user.check_password(password):
                    logger.warning(f"用户 {username} 密码错误")
                    return Response({
                        "code": 1,
                        "message": "用户名或密码错误",
                        "error": "Invalid credentials"
                    }, status=status.HTTP_401_UNAUTHORIZED)
                
            except CustomUser.DoesNotExist:
                logger.warning(f"用户 {username} 不存在")
                return Response({
                    "code": 1,
                    "message": "用户名或密码错误",
                    "error": "Invalid credentials"
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # 调用父类处理
            try:
                response = super().post(request, *args, **kwargs)
                
                if response.status_code == 200:
                    logger.info(f"用户 {username} 登录成功")
                    
                    # 确保返回标准格式的 token
                    if 'access' in response.data and 'refresh' in response.data:
                        # 已经是标准格式，直接包装
                        token_data = {
                            'access': response.data['access'],
                            'refresh': response.data['refresh']
                        }
                        return Response({
                            "code": 0,
                            "message": "登录成功",
                            "data": token_data
                        }, status=status.HTTP_200_OK)
                    else:
                        # 尝试解析非标准格式
                        logger.warning(f"非标准token响应格式: {response.data}")
                        return Response({
                            "code": 0,
                            "message": "登录成功",
                            "data": response.data
                        }, status=status.HTTP_200_OK)
                    
                logger.warning(f"用户 {username} 登录失败: {response.data}")
                return Response({
                    "code": 1,
                    "message": "用户名或密码错误",
                    "error": response.data
                }, status=response.status_code)
            except Exception as e:
                logger.error(f"Token生成失败: {str(e)}")
                logger.error(traceback.format_exc())
                return Response({
                    "code": 1,
                    "message": "Token生成失败",
                    "error": str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"登录处理发生异常: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                "code": 1,
                "message": f"服务器错误: {str(e)}",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 获取当前用户信息的视图示例 (需要认证)
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class CurrentUserView(APIView):
    """
    获取当前登录用户信息
    """
    permission_classes = [IsAuthenticated] # 要求用户必须登录

    def get(self, request):
        serializer = UserSerializer(request.user) # request.user 就是当前登录的用户对象
        return Response({"code": 0, "message": "获取成功", "data": serializer.data})
    
    def put(self, request):
        """
        更新当前用户信息
        """
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "code": 0,
                "message": "更新成功",
                "data": serializer.data
            })
        return Response({
            "code": 1,
            "message": "更新失败",
            "errors": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    """
    修改当前登录用户密码
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "code": 1,
                "message": "参数错误",
                "errors": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        old_password = serializer.validated_data['old_password']
        if not user.check_password(old_password):
            return Response({
                "code": 1,
                "message": "旧密码错误"
            }, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({
            "code": 0,
            "message": "密码修改成功"
        })