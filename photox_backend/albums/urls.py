from django.urls import path
from . import views

app_name = 'albums'

urlpatterns = [
    # 相册列表和创建
    path('', views.AlbumListView.as_view(), name='album-list'),
    # 相册详情、更新和删除
    path('<int:pk>/', views.AlbumDetailView.as_view(), name='album-detail'),
    # 相册图片管理
    path('<int:album_id>/images/', views.AlbumImageManageView.as_view(), name='album-images'),
]
