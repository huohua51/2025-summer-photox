from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import PermissionDenied

def admin_required(view_func):
    """需要管理员权限"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_admin():
            messages.error(request, '您没有权限访问此页面')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view

def moderator_required(view_func):
    """需要版主或管理员权限"""
    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not request.user.is_moderator():
            messages.error(request, '您没有权限访问此页面')
            raise PermissionDenied
        return view_func(request, *args, **kwargs)
    return wrapped_view

def permission_required(permission_name):
    """检查特定权限"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            if not getattr(request.user, permission_name, False):
                messages.error(request, '您没有此操作权限')
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator