# community/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, Prefetch
from django.contrib.auth import get_user_model
from .models import Comment, Like, Follow, Notification, Favorite
from .serializers import (
    CommentSerializer, LikeSerializer, FollowSerializer, 
    NotificationSerializer, UserSerializer, AlbumWithStatsSerializer
)
from albums.models import Album
from images.models import Image
from images.serializers import ImageSerializer
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from utils.sensitive_words import sensitive_filter

User = get_user_model()


class CommentViewSet(viewsets.ModelViewSet):
    """评论视图集"""
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        user_id = self.request.query_params.get('user', None)
        
        # 如果指定了用户ID
        if user_id is not None:
            # 如果是查看自己的评论，显示所有评论（包括未审核的）
            if str(user_id) == str(getattr(self.request.user, 'id', None)):
                queryset = Comment.objects.filter(user_id=user_id, is_deleted=False)
            else:
                # 查看其他用户的评论，只显示审核通过的
                queryset = Comment.objects.filter(user_id=user_id, is_deleted=False, is_approved=True)
        else:
            # 没有指定用户ID，显示当前用户的所有评论 + 其他用户的审核通过评论
            if self.request.user.is_authenticated:
                queryset = Comment.objects.filter(
                    Q(user=self.request.user, is_deleted=False) |  # 自己的所有评论
                    Q(is_deleted=False, is_approved=True)  # 其他用户的审核通过评论
                )
            else:
                # 未登录用户只能看到审核通过的评论
                queryset = Comment.objects.filter(is_deleted=False, is_approved=True)
        
        queryset = queryset.select_related('user', 'album', 'image', 'parent')
        queryset = queryset.prefetch_related(
            Prefetch('replies', queryset=Comment.objects.filter(is_deleted=False, is_approved=True))
        )
        album_id = self.request.query_params.get('album')
        image_id = self.request.query_params.get('image')
        if album_id:
            queryset = queryset.filter(album_id=album_id)
        elif image_id:
            queryset = queryset.filter(image_id=image_id)
        if self.action == 'list':
            queryset = queryset.filter(parent=None)
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        # 检查评论内容是否包含敏感词
        content = serializer.validated_data.get('content', '')
        if content:
            content_check = sensitive_filter.check_text(content)
            if content_check['has_sensitive']:
                # 记录敏感词检测日志
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"评论包含敏感词: {content_check['sensitive_words']}, 用户: {self.request.user.username}")
                # 使用过滤后的内容
                serializer.validated_data['content'] = content_check['filtered_text']
        
        serializer.save(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        """软删除评论"""
        comment = self.get_object()
        if comment.user != request.user:
            return Response({'error': '只能删除自己的评论'}, status=status.HTTP_403_FORBIDDEN)
        
        comment.is_deleted = True
        comment.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=True, methods=['get'])
    def replies(self, request, pk=None):
        """获取评论的所有回复"""
        comment = self.get_object()
        replies = comment.replies.filter(is_deleted=False).order_by('created_at')
        page = self.paginate_queryset(replies)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(replies, many=True)
        return Response(serializer.data)


class LikeViewSet(viewsets.GenericViewSet):
    """点赞视图集"""
    serializer_class = LikeSerializer
    permission_classes = [IsAuthenticated] #登录用户才可访问
    
    @action(detail=False, methods=['post'])
    def toggle(self, request):
        """切换点赞状态"""
        like_type = request.data.get('like_type')
        object_id = request.data.get('object_id')
        
        if not like_type or not object_id:
            return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已经点赞
        existing_like = Like.objects.filter(
            user=request.user,
            like_type=like_type,
            object_id=object_id
        ).first()
        
        if existing_like:
            # 取消点赞
            existing_like.delete()
            # 统计最新点赞数
            like_count = Like.objects.filter(like_type=like_type, object_id=object_id).count()
            return Response({'liked': False, 'like_count': like_count, 'message': '取消点赞成功'})
        else:
            # 点赞
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            # 统计最新点赞数
            like_count = Like.objects.filter(like_type=like_type, object_id=object_id).count()
            return Response({'liked': True, 'like_count': like_count, 'message': '点赞成功', 'data': serializer.data})
    
    @action(detail=False, methods=['get'])
    def check(self, request):
        """检查是否已点赞"""
        like_type = request.query_params.get('like_type')
        object_id = request.query_params.get('object_id')
        
        if not like_type or not object_id:
            return Response({'error': '缺少必要参数'}, status=status.HTTP_400_BAD_REQUEST)
        
        liked = Like.objects.filter(
            user=request.user,
            like_type=like_type,
            object_id=object_id
        ).exists()
        
        # 统计总点赞数
        like_count = Like.objects.filter(like_type=like_type, object_id=object_id).count()
        
        return Response({'liked': liked, 'like_count': like_count})


class FollowViewSet(viewsets.GenericViewSet):
    """关注视图集"""
    serializer_class = FollowSerializer
    permission_classes = [IsAuthenticated]
    
    @action(detail=True, methods=['post'])
    def toggle(self, request, pk=None):
        """切换关注状态"""
        following_user = get_object_or_404(User, pk=pk)
        
        if following_user == request.user:
            return Response({'error': '不能关注自己'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 检查是否已关注
        existing_follow = Follow.objects.filter(
            follower=request.user,
            following=following_user
        ).first()
        
        if existing_follow:
            # 取消关注
            existing_follow.delete()
            return Response({'following': False, 'message': '取消关注成功'})
        else:
            # 关注
            follow = Follow.objects.create(
                follower=request.user,
                following=following_user
            )
            
            # 创建通知
            Notification.objects.create(
                user=following_user,
                sender=request.user,
                notification_type='follow',
                content=f'{request.user.username} 关注了你'
            )
            
            serializer = self.get_serializer(follow)
            return Response({'following': True, 'message': '关注成功', 'data': serializer.data})
    
    @action(detail=True, methods=['get'])
    def followers(self, request, pk=None):
        """获取用户的粉丝列表"""
        user = get_object_or_404(User, pk=pk)
        followers = Follow.objects.filter(following=user).select_related('follower')
        page = self.paginate_queryset(followers)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(followers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def following(self, request, pk=None):
        """获取用户的关注列表"""
        user = get_object_or_404(User, pk=pk)
        following = Follow.objects.filter(follower=user).select_related('following')
        page = self.paginate_queryset(following)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(following, many=True)
        return Response(serializer.data)


class NotificationViewSet(viewsets.ModelViewSet):
    """通知视图集"""
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).select_related('sender')
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """标记所有通知为已读"""
        Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
        return Response({'message': '所有通知已标记为已读'})
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """标记单个通知为已读"""
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return Response({'message': '通知已标记为已读'})
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """获取未读通知数量"""
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """用户视图集"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @action(detail=True, methods=['get'])
    def albums(self, request, pk=None):
        """获取用户的相册列表"""
        user = self.get_object()
        albums = Album.objects.filter(user=user)
        
        # ORM聚合统计用comment（单数）
        albums = albums.annotate(
            comment_count=Count('comment', filter=Q(comment__is_deleted=False))
        )
        
        page = self.paginate_queryset(albums)
        if page is not None:
            serializer = AlbumWithStatsSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = AlbumWithStatsSerializer(albums, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """获取当前用户信息"""
        if not request.user.is_authenticated:
            return Response({'error': '未登录'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)


class FavoriteView(APIView):
    """收藏/取消收藏接口"""
    permission_classes = [IsAuthenticated]

    def post(self, request, image_id):
        """收藏图片"""
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"error": "图片不存在"}, status=status.HTTP_404_NOT_FOUND)

        # 检查是否已收藏
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            image=image
        )

        if created:
            return Response({
                "message": "收藏成功",
                "favorited": True
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                "message": "已经收藏过了",
                "favorited": True
            }, status=status.HTTP_200_OK)

    def delete(self, request, image_id):
        """取消收藏"""
        try:
            favorite = Favorite.objects.get(
                user=request.user,
                image_id=image_id
            )
            favorite.delete()
            return Response({
                "message": "取消收藏成功",
                "favorited": False
            }, status=status.HTTP_200_OK)
        except Favorite.DoesNotExist:
            return Response({
                "error": "未收藏此图片",
                "favorited": False
            }, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, image_id):
        """检查是否收藏"""
        is_favorited = Favorite.objects.filter(
            user=request.user,
            image_id=image_id
        ).exists()
        
        return Response({
            "favorited": is_favorited
        }, status=status.HTTP_200_OK)


class FavoriteListView(ListAPIView):
    """用户收藏列表"""
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = PageNumberPagination

    def get_queryset(self):
        # 获取当前用户的所有收藏图片
        return Image.objects.filter(
            favorited_by__user=self.request.user
        ).order_by('-favorited_by__created_at')