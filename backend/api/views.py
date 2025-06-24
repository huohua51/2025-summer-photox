from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate

class LoginView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        # 这里只是模拟登录，实际项目需要完整的认证逻辑
        if username == 'admin' and password == '123456':
            return Response({
                'success': True,
                'message': '登录成功',
                'user': {
                    'username': username,
                    'id': 1
                }
            })
        else:
            return Response({
                'success': False,
                'message': '用户名或密码错误'
            }, status=status.HTTP_401_UNAUTHORIZED)

class TestConnectionView(APIView):
    def get(self, request):
        return Response({
            'message': '前后端连接成功！',
            'status': 'connected'
        })
