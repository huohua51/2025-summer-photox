from django.utils import timezone
from .models import AdminLog

class AdminActionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # 记录管理员操作
        if request.user.is_authenticated and request.user.is_admin():
            if request.path.startswith('/admin/') and request.method == 'POST':
                AdminLog.objects.create(
                    user=request.user,
                    action=request.path,
                    method=request.method,
                    ip_address=self.get_client_ip(request),
                    timestamp=timezone.now()
                )
        
        return response
    
    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip