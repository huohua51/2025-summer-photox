# community/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, LikeViewSet, FollowViewSet, NotificationViewSet, UserViewSet, FavoriteView, FavoriteListView

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'likes', LikeViewSet, basename='like')
router.register(r'follows', FollowViewSet, basename='follow')
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'users', UserViewSet, basename='user')

app_name = 'community'  
urlpatterns = [
    path('', include(router.urls)),
    path('favorites/<int:image_id>/', FavoriteView.as_view(), name='favorite'),
    path('favorites/', FavoriteListView.as_view(), name='favorite-list'),
]
