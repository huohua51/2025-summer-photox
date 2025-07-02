# users/urls.py
from django.urls import path
from .views import RegisterView, CurrentUserView, CustomTokenObtainPairView, ChangePasswordView
# 导入 Simple JWT 提供的视图
from . import admin_views

from rest_framework_simplejwt.views import (
    # TokenObtainPairView, # 注释掉，使用自定义的
    TokenRefreshView,  # 刷新 Token
    TokenVerifyView,   # 验证 Token (可选)
)
# from .views import CustomTokenObtainPairView # 如果你自定义了登录视图

app_name = 'users' # 定义 app namespace (可选但推荐)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    # 使用自定义的登录视图
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    # 注释掉默认视图
    # path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'), # 可选
    path('me/', CurrentUserView.as_view(), name='current_user'), # 获取当前用户信息
    path('password/change/', ChangePasswordView.as_view(), name='change_password'),
       # 管理后台路由
    path('admin/dashboard/', admin_views.admin_dashboard, name='admin_dashboard'),
    path('admin/users/', admin_views.user_management, name='user_management'),
    path('admin/users/<int:user_id>/edit/', admin_views.edit_user, name='edit_user'),
    path('admin/users/<int:user_id>/delete/', admin_views.delete_user, name='delete_user'),
    path('admin/tags/', admin_views.tag_management, name='tag_management'),
    path('admin/templates/', admin_views.template_management, name='template_management'),
    path('admin/statistics/', admin_views.statistics, name='statistics'),
]