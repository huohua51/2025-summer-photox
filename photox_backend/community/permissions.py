# community/permissions.py
from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    对象级权限，只允许对象的所有者编辑它
    """
    
    def has_object_permission(self, request, view, obj):
        # 读取权限允许所有请求
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 写入权限只允许对象的所有者
        return obj.user == request.user


class IsCommentOwner(permissions.BasePermission):
    """
    评论所有者权限
    """
    
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 只有评论的作者才能修改或删除
        return obj.user == request.user


class IsNotificationOwner(permissions.BasePermission):
    """
    通知所有者权限
    """
    
    def has_object_permission(self, request, view, obj):
        # 只有通知的接收者才能查看和操作
        return obj.user == request.user