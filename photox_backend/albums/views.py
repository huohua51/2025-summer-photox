from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import Album
from .serializers import AlbumSerializer, AlbumCreateSerializer, AlbumUpdateSerializer
from images.models import Image

# Create your views here.

class AlbumListView(generics.ListCreateAPIView):
    """
    获取相册列表和创建新相册
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AlbumCreateSerializer
        return AlbumSerializer
    
    def get_queryset(self):
        return Album.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response({
            "code": 0,
            "message": "相册创建成功",
            "data": AlbumSerializer(serializer.instance).data
        }, status=status.HTTP_201_CREATED)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = AlbumSerializer(queryset, many=True)
        return Response({
            "code": 0,
            "message": "获取成功",
            "data": serializer.data
        })

class AlbumDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    获取、更新和删除单个相册
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AlbumSerializer
    
    def get_queryset(self):
        return Album.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return AlbumUpdateSerializer
        return AlbumSerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({
            "code": 0,
            "message": "获取成功",
            "data": serializer.data
        })
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response({
            "code": 0,
            "message": "更新成功",
            "data": AlbumSerializer(instance).data
        })
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "code": 0,
            "message": "删除成功"
        }, status=status.HTTP_200_OK)

class AlbumImageManageView(APIView):
    """
    管理相册中的图片（添加/移除）
    """
    permission_classes = [IsAuthenticated]
    
    def get_album(self, album_id):
        try:
            return Album.objects.get(id=album_id, user=self.request.user)
        except Album.DoesNotExist:
            return None
    
    def get_image(self, image_id):
        try:
            return Image.objects.get(id=image_id, user=self.request.user)
        except Image.DoesNotExist:
            return None
    
    def post(self, request, album_id):
        """
        添加图片到相册
        """
        album = self.get_album(album_id)
        if not album:
            return Response({
                "code": 1,
                "message": "相册不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        image_id = request.data.get('image_id')
        if not image_id:
            return Response({
                "code": 1,
                "message": "请提供图片ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image = self.get_image(image_id)
        if not image:
            return Response({
                "code": 1,
                "message": "图片不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        album.images.add(image)
        return Response({
            "code": 0,
            "message": "图片添加成功"
        })
    
    def delete(self, request, album_id):
        """
        从相册移除图片
        """
        album = self.get_album(album_id)
        if not album:
            return Response({
                "code": 1,
                "message": "相册不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        image_id = request.data.get('image_id')
        if not image_id:
            return Response({
                "code": 1,
                "message": "请提供图片ID"
            }, status=status.HTTP_400_BAD_REQUEST)
        
        image = self.get_image(image_id)
        if not image:
            return Response({
                "code": 1,
                "message": "图片不存在"
            }, status=status.HTTP_404_NOT_FOUND)
        
        album.images.remove(image)
        return Response({
            "code": 0,
            "message": "图片移除成功"
        })
