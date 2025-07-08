from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator
from .sensitive_words import sensitive_filter
import logging

logger = logging.getLogger(__name__)

class SensitiveWordsCheckView(APIView):
    """敏感词检测API"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """检测文本中的敏感词"""
        text = request.data.get('text', '').strip()
        
        if not text:
            return Response({
                'error': '文本内容不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            result = sensitive_filter.check_text(text)
            
            # 记录敏感词检测日志
            if result['has_sensitive']:
                logger.warning(f"用户 {request.user.username} 的文本包含敏感词: {result['sensitive_words']}")
            
            return Response({
                'has_sensitive': result['has_sensitive'],
                'sensitive_words': result['sensitive_words'],
                'filtered_text': result['filtered_text'],
                'replacement_count': result['replacement_count']
            })
            
        except Exception as e:
            logger.error(f"敏感词检测失败: {e}")
            return Response({
                'error': '敏感词检测失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class SensitiveWordsManagementView(APIView):
    """敏感词管理API（仅管理员）"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """获取敏感词列表"""
        try:
            words = sensitive_filter.get_sensitive_words()
            return Response({
                'words': words,
                'total_count': len(words)
            })
        except Exception as e:
            logger.error(f"获取敏感词列表失败: {e}")
            return Response({
                'error': '获取敏感词列表失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """添加敏感词"""
        word = request.data.get('word', '').strip()
        
        if not word:
            return Response({
                'error': '敏感词不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sensitive_filter.add_sensitive_word(word)
            sensitive_filter.save_sensitive_words()
            
            logger.info(f"管理员 {request.user.username} 添加敏感词: {word}")
            
            return Response({
                'message': f'敏感词 "{word}" 已添加',
                'word': word
            })
            
        except Exception as e:
            logger.error(f"添加敏感词失败: {e}")
            return Response({
                'error': '添加敏感词失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, word):
        """删除敏感词"""
        word = word.strip()
        
        if not word:
            return Response({
                'error': '敏感词不能为空'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            sensitive_filter.remove_sensitive_word(word)
            sensitive_filter.save_sensitive_words()
            
            logger.info(f"管理员 {request.user.username} 删除敏感词: {word}")
            
            return Response({
                'message': f'敏感词 "{word}" 已删除',
                'word': word
            })
            
        except Exception as e:
            logger.error(f"删除敏感词失败: {e}")
            return Response({
                'error': '删除敏感词失败'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 