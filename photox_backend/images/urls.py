app_name = 'images'

from django.urls import path
from .views import (
    ImageUploadView, ImageListView, ImageDetailView, ImageFeedView, 
    ImageAIAnalysisView, ai_description_view, ImageTagsView,
    ImageStyleAnalysisView, ImageRecommendationView, AIProcessView,
    AIProcessLocalView, DeleteProcessedImageView, BatchImageUploadView
)

urlpatterns = [
    path('upload/', ImageUploadView.as_view(), name='image-upload'),
    path('batch-upload/', BatchImageUploadView.as_view(), name='batch-image-upload'),
    path('', ImageListView.as_view(), name='image-list'),
    path('feed/', ImageFeedView.as_view(), name='image-feed'),
    path('recommendations/', ImageRecommendationView.as_view(), name='image-recommendations'),
    path('<int:image_id>/', ImageDetailView.as_view(), name='image-detail-delete'),
    path('<int:image_id>/ai-analysis/', ImageAIAnalysisView.as_view(), name='image-ai-analysis'),
    path('<int:image_id>/ai_description/', ai_description_view, name='ai_description'),
    path('<int:image_id>/tags/', ImageTagsView.as_view(), name='image-tags'),
    path('<int:image_id>/style-analysis/', ImageStyleAnalysisView.as_view(), name='image-style-analysis'),
    path('<int:image_id>/ai-process/', AIProcessView.as_view(), name='image-ai-process'),
    path('ai-process-local/', AIProcessLocalView.as_view(), name='image-ai-process-local'),
    path('delete-processed/', DeleteProcessedImageView.as_view(), name='delete-processed-image'),
]



