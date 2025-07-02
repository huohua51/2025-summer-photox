from django.urls import path
from . import admin_views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', admin_views.admin_dashboard, name='dashboard'),
    path('stats/', admin_views.quick_stats, name='quick_stats'),
    path('stats-dashboard/', admin_views.stats_dashboard, name='stats_dashboard'),
    path('batch-operations/', admin_views.batch_operations, name='batch_operations'),
    path('user-analytics/', admin_views.user_analytics, name='user_analytics'),
    path('content-moderation/', admin_views.content_moderation, name='content_moderation'),
    path('albums/album/', admin_views.album_management, name='album_management'),
] 