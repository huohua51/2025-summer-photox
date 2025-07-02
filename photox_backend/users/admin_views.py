from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from .models import CustomUser
from .decorators import admin_required, permission_required
from django.http import HttpResponse, JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import timedelta

from images.models import Image
from albums.models import Album
from community.models import Comment, Like, Follow, Notification

def tag_management(request):
    return HttpResponse("标签管理后台页面")

def template_management(request):   # ✅ 补上这一段
    return HttpResponse("模板管理后台页面")

@staff_member_required
def admin_dashboard(request):
    """管理员仪表板"""
    # 获取基本统计数据
    total_users = CustomUser.objects.count()
    total_images = Image.objects.count()
    total_albums = Album.objects.count()
    total_comments = Comment.objects.filter(is_deleted=False).count()
    
    # 获取最近30天的数据
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_users = CustomUser.objects.filter(date_joined__gte=thirty_days_ago).count()
    recent_images = Image.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_albums = Album.objects.filter(created_at__gte=thirty_days_ago).count()
    recent_comments = Comment.objects.filter(created_at__gte=thirty_days_ago, is_deleted=False).count()
    
    # 用户角色分布
    user_roles = CustomUser.objects.values('role').annotate(count=Count('role')).order_by('role')
    
    # 最活跃用户（按照上传图片数量）
    active_users = CustomUser.objects.annotate(
        images_count=Count('images'),
        albums_count=Count('albums'),
        comments_count=Count('comment', filter=Q(comment__is_deleted=False))
    ).filter(
        Q(images_count__gt=0) | Q(albums_count__gt=0) | Q(comments_count__gt=0)
    ).order_by('-images_count')[:10]
    
    # 最受欢迎的图片（按点赞数）
    from django.db.models import Subquery, OuterRef
    
    # 计算每张图片的点赞数
    image_likes = Like.objects.filter(
        like_type='image',
        object_id=OuterRef('id')
    ).values('object_id').annotate(
        likes_count=Count('id')
    ).values('likes_count')
    
    popular_images = Image.objects.annotate(
        likes_count=Subquery(image_likes)
    ).filter(
        likes_count__isnull=False
    ).order_by('-likes_count')[:10]
    
    # 如果没有点赞数据，显示最新的图片
    if not popular_images.exists():
        popular_images = Image.objects.order_by('-created_at')[:10]
        
    # 最热门标签统计
    import json
    all_tags = []
    for image in Image.objects.exclude(tags__isnull=True).exclude(tags=''):
        try:
            if image.tags:
                tags = image.get_tags_as_list()
                all_tags.extend(tags)
        except:
            # 如果解析失败，跳过
            continue
    
    # 统计标签频率
    from collections import Counter
    tag_counter = Counter(all_tags)
    popular_tags = tag_counter.most_common(10)  # 前10个热门标签
    
    # 最新的未读通知数量
    unread_notifications = Notification.objects.filter(is_read=False).count()
    
    # 待审核内容
    unverified_users = CustomUser.objects.filter(is_verified=False).count()
    public_images = Image.objects.filter(is_public=True).count()
    public_albums = Album.objects.filter(is_public=True).count()
    
    # 系统健康状态
    deleted_comments = Comment.objects.filter(is_deleted=True).count()
    orphaned_images = Image.objects.filter(albums__isnull=True).count()
    
    context = {
        'stats': {
            'total_users': total_users,
            'total_images': total_images,
            'total_albums': total_albums,
            'total_comments': total_comments,
            'recent_users': recent_users,
            'recent_images': recent_images,
            'recent_albums': recent_albums,
            'recent_comments': recent_comments,
            'unread_notifications': unread_notifications,
            'unverified_users': unverified_users,
            'public_images': public_images,
            'public_albums': public_albums,
            'deleted_comments': deleted_comments,
            'orphaned_images': orphaned_images,
        },
        'user_roles': list(user_roles),
        'active_users': active_users,
        'popular_images': popular_images,
        'popular_tags': popular_tags,
    }
    
    return render(request, 'admin/dashboard.html', context)

@staff_member_required
def quick_stats(request):
    """快速统计API"""
    if request.method == 'GET':
        try:
            today = timezone.now().date()
            
            # 今日注册用户数 (使用date_joined字段)
            users_today = CustomUser.objects.filter(
                date_joined__date=today
            ).count()
            
            # 今日上传图片数
            images_today = Image.objects.filter(
                created_at__date=today
            ).count()
            
            # 今日评论数
            comments_today = Comment.objects.filter(
                created_at__date=today,
                is_deleted=False
            ).count()
            
            # 未读通知数
            unread_notifications = Notification.objects.filter(
                is_read=False
            ).count()
            
            # 添加更多统计信息
            total_users = CustomUser.objects.count()
            total_images = Image.objects.count()
            total_albums = Album.objects.count()
            total_comments = Comment.objects.filter(is_deleted=False).count()
            
            # 今日创建的相册数
            albums_today = Album.objects.filter(
                created_at__date=today
            ).count()
            
            stats = {
                'users_today': users_today,
                'images_today': images_today,
                'comments_today': comments_today,
                'albums_today': albums_today,
                'unread_notifications': unread_notifications,
                'total_users': total_users,
                'total_images': total_images,
                'total_albums': total_albums,
                'total_comments': total_comments,
                'date': today.strftime('%Y-%m-%d'),
            }
            
        except Exception as e:
            # 如果查询失败，返回默认数据
            stats = {
                'users_today': 0,
                'images_today': 0,
                'comments_today': 0,
                'albums_today': 0,
                'unread_notifications': 0,
                'total_users': CustomUser.objects.count(),
                'total_images': Image.objects.count(),
                'total_albums': Album.objects.count(),
                'total_comments': Comment.objects.filter(is_deleted=False).count(),
                'date': timezone.now().date().strftime('%Y-%m-%d'),
                'error': str(e)
            }
        
        return JsonResponse(stats)

@staff_member_required
def batch_operations(request):
    """批量操作"""
    if request.method == 'POST':
        operation = request.POST.get('operation')
        
        if operation == 'verify_recent_users':
            # 验证有内容贡献的用户（上传过图片或创建过相册）
            updated = CustomUser.objects.annotate(
                content_count=Count('images') + Count('albums')
            ).filter(
                content_count__gt=0,
                is_verified=False
            ).update(is_verified=True)
            messages.success(request, f'成功验证了 {updated} 个有内容贡献的用户。')
            
        elif operation == 'clean_old_notifications':
            # 清理30天前的已读通知
            thirty_days_ago = timezone.now() - timedelta(days=30)
            deleted, _ = Notification.objects.filter(
                created_at__lt=thirty_days_ago,
                is_read=True
            ).delete()
            messages.success(request, f'成功清理了 {deleted} 条旧通知。')
            
        elif operation == 'restore_recent_comments':
            # 恢复最近被删除的评论
            seven_days_ago = timezone.now() - timedelta(days=7)
            updated = Comment.objects.filter(
                updated_at__gte=seven_days_ago,
                is_deleted=True
            ).update(is_deleted=False)
            messages.success(request, f'成功恢复了 {updated} 条最近删除的评论。')
            
        return JsonResponse({'status': 'success'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@staff_member_required
def user_analytics(request):
    """美观的用户分析仪表板"""
    try:
        today = timezone.now().date()
        
        # 用户增长趋势 - 最近12个月
        growth_data = []
        for i in range(12, 0, -1):
            month_date = today.replace(day=1) - timedelta(days=30*i)
            try:
                month_str = month_date.strftime('%Y-%m')
                count = CustomUser.objects.filter(
                    date_joined__year=month_date.year,
                    date_joined__month=month_date.month
                ).count()
                growth_data.append({
                    'month': month_str,
                    'month_name': month_date.strftime('%m月'),
                    'count': count
                })
            except:
                growth_data.append({
                    'month': month_date.strftime('%Y-%m'),
                    'month_name': month_date.strftime('%m月'),
                    'count': 0
                })
        
        # 用户基本统计
        user_stats = {
            'total': CustomUser.objects.count(),
            'active': CustomUser.objects.filter(is_active=True).count(),
            'verified': CustomUser.objects.filter(is_verified=True).count(),
            'today_joined': CustomUser.objects.filter(date_joined__date=today).count(),
            'this_week': CustomUser.objects.filter(date_joined__gte=today - timedelta(days=7)).count(),
            'this_month': CustomUser.objects.filter(date_joined__gte=today - timedelta(days=30)).count(),
        }
        
        # 用户角色分布
        role_distribution = []
        for role, name in CustomUser.ROLE_CHOICES:
            count = CustomUser.objects.filter(role=role).count()
            if count > 0:
                percentage = round((count / user_stats['total']) * 100, 1) if user_stats['total'] > 0 else 0
                role_distribution.append({
                    'role': name,
                    'count': count,
                    'percentage': percentage
                })
        
        # 用户活跃度分析
        activity_levels = []
        users_with_content = CustomUser.objects.annotate(
            total_images=Count('images'),
            total_albums=Count('albums'),
            total_comments=Count('comment', filter=Q(comment__is_deleted=False))
        )
        
        # 高度活跃用户 (有图片、相册或评论)
        highly_active = users_with_content.filter(
            Q(total_images__gte=5) | Q(total_albums__gte=3) | Q(total_comments__gte=10)
        ).count()
        
        # 中度活跃用户
        moderately_active = users_with_content.filter(
            Q(total_images__gte=1, total_images__lt=5) | 
            Q(total_albums__gte=1, total_albums__lt=3) | 
            Q(total_comments__gte=1, total_comments__lt=10)
        ).count()
        
        # 低活跃用户 (注册了但没有内容)
        low_active = CustomUser.objects.annotate(
            total_content=Count('images') + Count('albums') + Count('comment', filter=Q(comment__is_deleted=False))
        ).filter(total_content=0).count()
        
        activity_levels = [
            {'level': '高度活跃', 'count': highly_active, 'color': '#4caf50'},
            {'level': '中度活跃', 'count': moderately_active, 'color': '#ff9800'},
            {'level': '低活跃', 'count': low_active, 'color': '#f44336'},
        ]
        
        # 最活跃用户 TOP 10
        top_users = CustomUser.objects.annotate(
            images_count=Count('images'),
            albums_count=Count('albums'),
            comments_count=Count('comment', filter=Q(comment__is_deleted=False)),
            total_activity=Count('images') + Count('albums') + Count('comment', filter=Q(comment__is_deleted=False))
        ).filter(total_activity__gt=0).order_by('-total_activity')[:10]
        
        # 新用户趋势 (最近7天)
        recent_users = []
        for i in range(7, 0, -1):
            date = today - timedelta(days=i-1)
            count = CustomUser.objects.filter(date_joined__date=date).count()
            recent_users.append({
                'date': date.strftime('%m-%d'),
                'count': count,
                'weekday': date.strftime('%a')
            })
        
        # 用户权限统计
        permission_stats = {
            'manage_users': CustomUser.objects.filter(can_manage_users=True).count(),
            'manage_tags': CustomUser.objects.filter(can_manage_tags=True).count(),
            'manage_templates': CustomUser.objects.filter(can_manage_templates=True).count(),
            'view_statistics': CustomUser.objects.filter(can_view_statistics=True).count(),
        }
        
        # 用户内容统计
        content_stats = []
        for user in CustomUser.objects.annotate(
            images_count=Count('images'),
            albums_count=Count('albums'),
            comments_count=Count('comment', filter=Q(comment__is_deleted=False))
        ).filter(
            Q(images_count__gt=0) | Q(albums_count__gt=0) | Q(comments_count__gt=0)
        ).order_by('-images_count')[:15]:
            content_stats.append({
                'username': user.username,
                'images': user.images_count,
                'albums': user.albums_count,
                'comments': user.comments_count,
                'join_date': user.date_joined,
                'is_verified': user.is_verified,
                'role': user.get_role_display(),
            })
        
        # 最新注册用户
        latest_users = CustomUser.objects.order_by('-date_joined')[:8]
        
        context = {
            'user_stats': user_stats,
            'growth_data': growth_data,
            'role_distribution': role_distribution,
            'activity_levels': activity_levels,
            'top_users': top_users,
            'recent_users': recent_users,
            'permission_stats': permission_stats,
            'content_stats': content_stats,
            'latest_users': latest_users,
            'current_date': today,
        }
        
    except Exception as e:
        # 错误处理
        context = {
            'error': str(e),
            'user_stats': {'total': 0, 'active': 0, 'verified': 0, 'today_joined': 0, 'this_week': 0, 'this_month': 0},
            'growth_data': [],
            'role_distribution': [],
            'activity_levels': [],
            'top_users': [],
            'recent_users': [],
            'permission_stats': {'manage_users': 0, 'manage_tags': 0, 'manage_templates': 0, 'view_statistics': 0},
            'content_stats': [],
            'latest_users': [],
            'current_date': timezone.now().date(),
        }
    
    return render(request, 'admin/user_analytics_dashboard.html', context)

@staff_member_required  
def content_moderation(request):
    """内容审核页面"""
    # 需要审核的内容
    pending_verification = {
        'users': CustomUser.objects.filter(is_verified=False).count(),
        'public_images': Image.objects.filter(is_public=True).count(),
        'public_albums': Album.objects.filter(is_public=True).count(),
        'reported_comments': Comment.objects.filter(is_deleted=False).count(),  # 这里可以添加举报机制
    }
    
    # 最近的活动
    recent_activities = {
        'new_users': CustomUser.objects.order_by('-date_joined')[:5],
        'new_images': Image.objects.order_by('-created_at')[:5],
        'new_comments': Comment.objects.filter(is_deleted=False).order_by('-created_at')[:5],
    }
    
    context = {
        'pending_verification': pending_verification,
        'recent_activities': recent_activities,
    }
    
    return render(request, 'admin/content_moderation.html', context)

@staff_member_required
def album_management(request):
    """相册管理页面"""
    # 获取所有相册，支持搜索和筛选
    albums = Album.objects.all().select_related('user').prefetch_related('images')
    
    # 搜索功能
    search_query = request.GET.get('search', '')
    if search_query:
        albums = albums.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(user__username__icontains=search_query)
        )
    
    # 过滤器
    is_public = request.GET.get('is_public', '')
    if is_public:
        albums = albums.filter(is_public=is_public.lower() == 'true')
    
    albums = albums.order_by('-created_at')
    
    # 分页
    paginator = Paginator(albums, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # 统计数据
    stats = {
        'total_albums': Album.objects.count(),
        'public_albums': Album.objects.filter(is_public=True).count(),
        'private_albums': Album.objects.filter(is_public=False).count(),
        'empty_albums': Album.objects.filter(images__isnull=True).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'is_public': is_public,
        'stats': stats,
    }
    
    return render(request, 'admin/album_management.html', context)

@login_required
@permission_required('can_manage_users')
def user_management(request):
    """用户管理"""
    search_query = request.GET.get('search', '')
    role_filter = request.GET.get('role', '')
    
    users = CustomUser.objects.all()
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if role_filter:
        users = users.filter(role=role_filter)
    
    users = users.order_by('-created_at')
    
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'role_filter': role_filter,
    }
    return render(request, 'admin/user_management.html', context)

@login_required
@permission_required('can_manage_users')
def edit_user(request, user_id):
    """编辑用户"""
    user = get_object_or_404(CustomUser, pk=user_id)
    
    if request.method == 'POST':
        # 更新用户信息
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.role = request.POST.get('role', 'user')
        user.is_active = request.POST.get('is_active') == 'on'
        user.is_verified = request.POST.get('is_verified') == 'on'
        
        # 更新权限
        user.can_manage_users = request.POST.get('can_manage_users') == 'on'
        user.can_manage_tags = request.POST.get('can_manage_tags') == 'on'
        user.can_manage_templates = request.POST.get('can_manage_templates') == 'on'
        user.can_view_statistics = request.POST.get('can_view_statistics') == 'on'
        
        user.save()
        messages.success(request, '用户信息已更新')
        return redirect('user_management')
    
    return render(request, 'admin/edit_user.html', {'user': user})

@login_required
@permission_required('can_manage_users')
def delete_user(request, user_id):
    """删除用户"""
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, pk=user_id)
        if user == request.user:
            messages.error(request, '不能删除自己的账户')
        else:
            user.delete()
            messages.success(request, '用户已删除')
    return redirect('user_management')

@login_required
@permission_required('can_view_statistics')
def statistics(request):
    """统计页面"""
    # 获取各种统计数据
    context = {
        'total_users': CustomUser.objects.count(),
        'active_users': CustomUser.objects.filter(is_active=True).count(),
        'inactive_users': CustomUser.objects.filter(is_active=False).count(),
        'verified_users': CustomUser.objects.filter(is_verified=True).count(),
        'unverified_users': CustomUser.objects.filter(is_verified=False).count(),
        
        # 按角色统计
        'admin_count': CustomUser.objects.filter(role='admin').count(),
        'user_count': CustomUser.objects.filter(role='user').count(),
        
        # 最近注册用户
        'recent_users': CustomUser.objects.order_by('-created_at')[:5],
        
        # 权限统计
        'users_with_manage_users': CustomUser.objects.filter(can_manage_users=True).count(),
        'users_with_manage_tags': CustomUser.objects.filter(can_manage_tags=True).count(),
        'users_with_manage_templates': CustomUser.objects.filter(can_manage_templates=True).count(),
        'users_with_view_statistics': CustomUser.objects.filter(can_view_statistics=True).count(),
    }
    
    return render(request, 'admin/statistics.html', context)

@staff_member_required
def stats_dashboard(request):
    """美观的HTML统计仪表板"""
    try:
        today = timezone.now().date()
        
        # 今日统计
        today_stats = {
            'users': CustomUser.objects.filter(date_joined__date=today).count(),
            'images': Image.objects.filter(created_at__date=today).count(),
            'albums': Album.objects.filter(created_at__date=today).count(),
            'comments': Comment.objects.filter(created_at__date=today, is_deleted=False).count(),
        }
        
        # 总体统计
        total_stats = {
            'users': CustomUser.objects.count(),
            'images': Image.objects.count(),
            'albums': Album.objects.count(),
            'comments': Comment.objects.filter(is_deleted=False).count(),
            'unread_notifications': Notification.objects.filter(is_read=False).count(),
        }
        
        # 最近7天的统计
        seven_days_ago = timezone.now() - timedelta(days=7)
        recent_stats = {
            'users': CustomUser.objects.filter(date_joined__gte=seven_days_ago).count(),
            'images': Image.objects.filter(created_at__gte=seven_days_ago).count(),
            'albums': Album.objects.filter(created_at__gte=seven_days_ago).count(),
            'comments': Comment.objects.filter(created_at__gte=seven_days_ago, is_deleted=False).count(),
        }
        
        # 用户角色分布
        user_roles = []
        for role, name in CustomUser.ROLE_CHOICES:
            count = CustomUser.objects.filter(role=role).count()
            if count > 0:
                user_roles.append({'role': name, 'count': count})
        
        # 图片状态分布
        image_stats = {
            'public': Image.objects.filter(is_public=True).count(),
            'private': Image.objects.filter(is_public=False).count(),
        }
        
        # 相册状态分布
        album_stats = {
            'public': Album.objects.filter(is_public=True).count(),
            'private': Album.objects.filter(is_public=False).count(),
            'empty': Album.objects.filter(images__isnull=True).count(),
        }
        
        # 最活跃用户 (按图片数量)
        active_users = CustomUser.objects.annotate(
            images_count=Count('images'),
            albums_count=Count('albums')
        ).filter(images_count__gt=0).order_by('-images_count')[:5]
        
        # 最新用户
        latest_users = CustomUser.objects.order_by('-date_joined')[:5]
        
        # 最新图片
        latest_images = Image.objects.order_by('-created_at')[:5]
        
        context = {
            'today_stats': today_stats,
            'total_stats': total_stats,
            'recent_stats': recent_stats,
            'user_roles': user_roles,
            'image_stats': image_stats,
            'album_stats': album_stats,
            'active_users': active_users,
            'latest_users': latest_users,
            'latest_images': latest_images,
            'current_date': today,
        }
        
    except Exception as e:
        # 错误处理
        context = {
            'error': str(e),
            'today_stats': {'users': 0, 'images': 0, 'albums': 0, 'comments': 0},
            'total_stats': {'users': 0, 'images': 0, 'albums': 0, 'comments': 0, 'unread_notifications': 0},
            'recent_stats': {'users': 0, 'images': 0, 'albums': 0, 'comments': 0},
            'user_roles': [],
            'image_stats': {'public': 0, 'private': 0},
            'album_stats': {'public': 0, 'private': 0, 'empty': 0},
            'active_users': [],
            'latest_users': [],
            'latest_images': [],
            'current_date': timezone.now().date(),
        }
    
    return render(request, 'admin/stats_dashboard.html', context)

