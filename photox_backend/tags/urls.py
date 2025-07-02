from django.urls import path
from . import views

app_name = 'tags'

urlpatterns = [
    path('', views.TagListCreateView.as_view(), name='tag-list'),
    path('<int:id>/', views.TagDetailView.as_view(), name='tag-detail'),
    path('import/', views.TagImportView.as_view(), name='tag-import'),
]