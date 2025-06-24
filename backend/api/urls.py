from django.urls import path
from .views import LoginView, TestConnectionView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('test/', TestConnectionView.as_view(), name='test'),
]
