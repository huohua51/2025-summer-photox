# views.py
from django.conf import settings  # 导入 settings
from django.core.files.storage import FileSystemStorage
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.parsers import MultiPartParser
import time
import json
import logging
import traceback
import os
import shutil
from django.db import models
from rest_framework.decorators import api_view, action
import tempfile
from PIL import Image as PILImage
import requests
import random


from .pro import enhance_image, super_resolution, denoise_image, color_enhance_image
from .solve import adjust_brightness, adjust_contrast, adjust_saturation, adjust_hue, adjust_sharpness, adjust_blur
from ai_image import ai_image
from .delete import delete_image_from_cloud
from .models import Image
from .serializers import ImageUploadSerializer, ImageSerializer
from .ai.save import upload_and_set_metadata  # 七牛云上传工具
from .tasks import ai_image_analysis
from .ai.ai_classify import image_classification
from .ai.color import extract_colors_with_colorthief
from .ai.description import generate_image_description
logger = logging.getLogger(__name__)

def welcome_view(request):
    return HttpResponse("Welcome to Photox API!")

class ImageUploadView(APIView):
    permission_classes = [IsAuthenticated]  # 只有认证用户才能上传
    parser_classes = [MultiPartParser]  # 处理 multipart/form-data 请求

    def post(self, request, *args, **kwargs):
        logger.info("开始处理图片上传请求...")
        try:
            # 记录请求信息
            logger.info(f"用户 {request.user.username} 尝试上传图片")
            logger.info(f"请求内容类型: {request.content_type}")
            logger.info(f"请求文件数量: {len(request.FILES)}")
            
            serializer = ImageUploadSerializer(data=request.data)
            
            if not serializer.is_valid():
                logger.warning(f"表单数据验证失败: {serializer.errors}")
                return Response({
                    "code": 1,
                    "message": "表单数据验证失败",
                    "errors": serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
            logger.info("表单数据验证通过")
            
            # 检查是否有图片文件
            if 'image' not in request.FILES:
                logger.warning("请求中没有图片文件")
                return Response({
                    "code": 1,
                    "message": "没有提供图片文件"
                }, status=status.HTTP_400_BAD_REQUEST)
                
            # 获取上传的图片文件
            image_file = request.FILES['image']
            logger.info(f"接收到上传的图片: {image_file.name}, 大小: {image_file.size} 字节")
            
            # 正式处理逻辑
            try:
                # 使用 FileSystemStorage 保存文件，生成临时路径
                fs = FileSystemStorage(location='/tmp')  # 存储到临时目录
                tmp_file_path = fs.save(image_file.name, image_file)  # 保存到临时目录
                tmp_file_path = fs.path(tmp_file_path)  # 获取文件的绝对路径
                logger.info(f"图片已保存到临时路径: {tmp_file_path}")

                # 使用原始图片名称或生成唯一文件名
                safe_filename = os.path.basename(image_file.name).replace(' ', '_')
                file_name = f"images/{str(time.time()).replace('.', '')}_{safe_filename}"
                logger.info(f"在七牛云中的存储路径: {file_name}")

                # 从环境变量获取七牛云的配置
                access_key = settings.QINIU_ACCESS_KEY
                secret_key = settings.QINIU_SECRET_KEY
                bucket_name = settings.QINIU_BUCKET_NAME
                # api_key = "sk-ff8f03a8cfbc03d7df75b7ddb6b1fb7f0bfc8116e02986306865aa9149741301"
                api_key = "sk-3658ae5ea3284ff4865227db05f4a214"
                colors = extract_colors_with_colorthief(tmp_file_path, num_colors=2)

                # 更新AI分类调用，使用新的参数格式
                result = image_classification(
                    image_path=tmp_file_path,
                    api_key=api_key,
                    # model_id=3,
                    classes_file="ai/classes.txt",
                    # model_file="ai/model.txt"
                )
                category_id = result['category_id']
                tags = [tag['name'] for tag in result['tags']]
                logger.info(f"七牛云配置信息 - Access Key: {access_key[:5]}..., Bucket: {bucket_name}")

                if not all([access_key, secret_key, bucket_name]):
                    logger.error("七牛云配置不完整")
                    return Response({
                        "code": 1,
                        "message": "七牛云配置不完整，请配置环境变量"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # 尝试AI分析，如果失败则使用默认值
                try:
                    logger.info("开始AI分析图片...")
                    # tags, category = ai_image(tmp_file_path)
                    # logger.info(f"AI分析结果 - 标签: {tags}, 分类: {category}")
                except Exception as e:
                    logger.error(f"AI分析图片失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    tags = ["未分类"]
                    category = "其他"
                    logger.info("使用默认标签和分类")

                 

                # 上传图片到七牛云并获取外链 URL
                try:
                    logger.info("开始上传图片到七牛云...")
                    image_url = upload_and_set_metadata(
                        access_key=access_key,
                        secret_key=secret_key,
                        bucket_name=bucket_name,
                        file_path=tmp_file_path,  # 传递临时文件的绝对路径
                        key=file_name,  # 七牛云中的路径+文件名
                    )
                    logger.info(f"上传结果 - URL: {image_url}")
                except Exception as e:
                    logger.error(f"上传到七牛云时发生异常: {str(e)}")
                    logger.error(traceback.format_exc())
                    # 删除临时文件
                    if os.path.exists(tmp_file_path):
                        fs.delete(tmp_file_path)
                    return Response({
                        "code": 1,
                        "message": f"上传到七牛云失败: {str(e)}"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # 删除临时文件
                logger.info("删除临时文件...")
                if os.path.exists(tmp_file_path):
                    fs.delete(tmp_file_path)

                if not image_url:
                    logger.error("图片URL为空")
                    return Response({
                        "code": 1,
                        "message": "上传到七牛云失败，未获取到图片URL"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # 保存图片信息到数据库
                try:
                    logger.info("将图片信息保存到数据库...")
                    # 将标签列表转换为JSON字符串
                    tags_json = json.dumps(tags, ensure_ascii=False)
                    
                    image = Image.objects.create(
                        image_url=image_url,
                        title=serializer.validated_data.get('title', ''),
                        tags=tags_json,  # 存储为JSON字符串
                        user=request.user,  # 上传者为当前认证的用户
                        is_public=serializer.validated_data.get('is_public', False),
                        category_id=category_id,  # 使用 category_id
                        colors=colors  # 添加颜色数据
                    )
                    logger.info(f"数据库保存成功，图片ID: {image.id}")

                    # 自动创建对应类别的相册并添加图片
                    try:
                        # 获取类别名称
                        category_name = result['category_name']

                        # 查找或创建对应类别的相册
                        from albums.models import Album
                        album, created = Album.objects.get_or_create(
                            title=f"{category_name}相册",
                            user=request.user,
                            defaults={
                                'description': f'自动创建的{category_name}分类相册',
                                'is_public': False
                            }
                        )

                        # 将图片添加到相册
                        album.images.add(image)
                        logger.info(f"图片已添加到{category_name}相册")

                    except Exception as e:
                        logger.error(f"自动添加到相册失败: {str(e)}")
                        logger.error(traceback.format_exc())
                        # 这里我们不抛出异常，因为图片上传本身是成功的

                    # 构造成功响应
                    response_data = ImageSerializer(image).data  # 直接返回图片的序列化数据
                    logger.info("上传流程完成，返回成功响应")
                    return Response(response_data, status=status.HTTP_201_CREATED)
                except Exception as e:
                    logger.error(f"保存图片信息到数据库失败: {str(e)}")
                    logger.error(traceback.format_exc())
                    return Response({
                        "code": 1,
                        "message": f"保存图片信息到数据库失败: {str(e)}"
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            except Exception as e:
                logger.error(f"图片上传处理过程中发生未预期的异常: {str(e)}")
                logger.error(traceback.format_exc())
                return Response({
                    "code": 1,
                    "message": f"服务器内部错误: {str(e)}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
        except Exception as e:
            logger.error(f"处理请求时发生异常: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                "code": 1,
                "message": f"服务器错误: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class BatchImageUploadView(APIView):
    """批量图片上传视图"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        logger.info("开始处理批量图片上传请求...")
        try:
            # 记录请求信息
            logger.info(f"用户 {request.user.username} 尝试批量上传图片")
            logger.info(f"请求文件数量: {len(request.FILES)}")
            
            # 检查是否有图片文件
            if not request.FILES:
                logger.warning("请求中没有图片文件")
                return Response({
                    "code": 1,
                    "message": "没有提供图片文件"
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 获取所有上传的图片文件
            image_files = request.FILES.getlist('images')  # 支持多个文件
            if not image_files:
                # 如果没有images字段，尝试获取单个image字段
                if 'image' in request.FILES:
                    image_files = [request.FILES['image']]
                else:
                    return Response({
                        "code": 1,
                        "message": "没有提供图片文件"
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"接收到 {len(image_files)} 个图片文件")
            
            # 获取上传参数
            title = request.data.get('title', '')
            is_public = request.data.get('is_public', 'false').lower() == 'true'
            
            # 批量处理结果
            results = []
            errors = []
            
            # 从环境变量获取七牛云的配置
            access_key = settings.QINIU_ACCESS_KEY
            secret_key = settings.QINIU_SECRET_KEY
            bucket_name = settings.QINIU_BUCKET_NAME
            api_key = "sk-3658ae5ea3284ff4865227db05f4a214"
            
            if not all([access_key, secret_key, bucket_name]):
                logger.error("七牛云配置不完整")
                return Response({
                    "code": 1,
                    "message": "七牛云配置不完整，请配置环境变量"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # 批量处理每个文件
            for index, image_file in enumerate(image_files):
                try:
                    logger.info(f"处理第 {index + 1} 个文件: {image_file.name}")
                    
                    # 使用 FileSystemStorage 保存文件，生成临时路径
                    fs = FileSystemStorage(location='/tmp')
                    tmp_file_path = fs.save(image_file.name, image_file)
                    tmp_file_path = fs.path(tmp_file_path)
                    logger.info(f"图片已保存到临时路径: {tmp_file_path}")

                    # 使用原始图片名称或生成唯一文件名
                    safe_filename = os.path.basename(image_file.name).replace(' ', '_')
                    file_name = f"images/{str(time.time()).replace('.', '')}_{safe_filename}"
                    
                    # AI分析
                    colors = extract_colors_with_colorthief(tmp_file_path, num_colors=2)
                    result = image_classification(
                        image_path=tmp_file_path,
                        api_key=api_key,
                        classes_file="ai/classes.txt",
                    )
                    category_id = result['category_id']
                    tags = [tag['name'] for tag in result['tags']]
                    
                    # 上传到七牛云
                    image_url = upload_and_set_metadata(
                        access_key=access_key,
                        secret_key=secret_key,
                        bucket_name=bucket_name,
                        file_path=tmp_file_path,
                        key=file_name,
                    )
                    
                    # 删除临时文件
                    if os.path.exists(tmp_file_path):
                        fs.delete(tmp_file_path)
                    
                    if not image_url:
                        raise Exception("上传到七牛云失败，未获取到图片URL")
                    
                    # 保存到数据库
                    tags_json = json.dumps(tags, ensure_ascii=False)
                    file_title = title or image_file.name
                    
                    image = Image.objects.create(
                        image_url=image_url,
                        title=file_title,
                        tags=tags_json,
                        user=request.user,
                        is_public=is_public,
                        category_id=category_id,
                        colors=colors
                    )
                    
                    # 自动添加到相册
                    try:
                        category_name = result['category_name']
                        from albums.models import Album
                        album, created = Album.objects.get_or_create(
                            title=f"{category_name}相册",
                            user=request.user,
                            defaults={
                                'description': f'自动创建的{category_name}分类相册',
                                'is_public': False
                            }
                        )
                        album.images.add(image)
                    except Exception as e:
                        logger.error(f"自动添加到相册失败: {str(e)}")
                    
                    # 添加到成功结果
                    results.append(ImageSerializer(image).data)
                    logger.info(f"第 {index + 1} 个文件处理成功")
                    
                except Exception as e:
                    logger.error(f"处理第 {index + 1} 个文件失败: {str(e)}")
                    errors.append({
                        "file": image_file.name,
                        "error": str(e)
                    })
                    # 清理临时文件
                    if 'tmp_file_path' in locals() and os.path.exists(tmp_file_path):
                        fs.delete(tmp_file_path)
            
            # 返回批量处理结果
            response_data = {
                "code": 0,
                "message": f"批量上传完成，成功 {len(results)} 个，失败 {len(errors)} 个",
                "success_count": len(results),
                "error_count": len(errors),
                "results": results,
                "errors": errors
            }
            
            if errors:
                return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
            else:
                return Response(response_data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            logger.error(f"批量上传处理时发生异常: {str(e)}")
            logger.error(traceback.format_exc())
            return Response({
                "code": 1,
                "message": f"服务器错误: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ImageListView(ListAPIView):
    serializer_class = ImageSerializer  # 使用已有的序列化器

    # 自定义分页类，控制每页返回的图片数量
    class CustomPagination(PageNumberPagination):
        page_size = 10  # 默认每页显示10个图片
        page_size_query_param = 'page_size'
        max_page_size = 50  # 最大每页50个图片

    pagination_class = CustomPagination

    def get_permissions(self):
        # 如果请求公开图片，不需要认证
        is_public = self.request.query_params.get('is_public', None)
        if is_public is not None and str(is_public).lower() == 'true':
            return []
        # 否则需要认证
        return [IsAuthenticated()]


    def get_queryset(self):
        # 获取查询参数
        is_public = self.request.query_params.get('is_public', None)
        user_id = self.request.query_params.get('user', None)  # 兼容 user_id/user
        if user_id is None:
            user_id = self.request.query_params.get('user_id', None)
        
        queryset = Image.objects.all()
        # 按用户过滤
        if user_id is not None:
            queryset = queryset.filter(user_id=user_id)
            if str(user_id) != str(getattr(self.request.user, 'id', None)):
                if is_public is None:
                    queryset = queryset.filter(is_public=True)
        if user_id is None:
            if is_public is not None:
                is_public = str(is_public).lower() == 'true'
                queryset = queryset.filter(is_public=is_public)
            else:
                if self.request.user.is_authenticated:
                    queryset = queryset.filter(user=self.request.user)
                else:
                    queryset = Image.objects.none()
        else:
            if is_public is not None:
                is_public = str(is_public).lower() == 'true'
                queryset = queryset.filter(is_public=is_public)

        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)

        exclude_id = self.request.query_params.get('exclude_id')
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)

        # ====== 热门推荐逻辑：用Subquery统计点赞数并降序排序 ======
        order_by = self.request.query_params.get('order_by')
        if order_by == 'like_count':
            from django.db.models import Subquery, OuterRef, IntegerField, Count
            from community.models import Like
            like_count_subquery = Like.objects.filter(
                like_type='image',
                object_id=OuterRef('id')
            ).values('object_id').annotate(
                cnt=Count('id')
            ).values('cnt')
            queryset = queryset.annotate(
                like_count=Subquery(like_count_subquery, output_field=IntegerField())
            ).order_by('-like_count', '-created_at')

        # ====== 相似内容推荐逻辑：只要有一个标签相同就推荐 ======
        tags = self.request.query_params.get('tags')
        if tags:
            tag_list = [t.strip() for t in tags.split(',') if t.strip()]
            queryset = [img for img in queryset if any(
                tag in img.get_tags_as_list() for tag in tag_list
            )]

        limit = self.request.query_params.get('limit')
        if limit:
            queryset = list(queryset)[:int(limit)]

        return queryset


    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def get_serializer_context(self):
        """为序列化器提供上下文"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ImageDetailView(APIView):
    permission_classes = [IsAuthenticated]  # 需要认证

    # GET 请求，获取图片详情
    def get(self, request, image_id):
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"code": 1, "message": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ImageSerializer(image, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PUT 请求，修改图片信息
    def put(self, request, image_id):
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"code": 1, "message": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        if image.user != request.user:
            raise PermissionDenied("You do not have permission to edit this image.")

        title = request.data.get('title', None)
        is_public = request.data.get('is_public', None)

        if title:
            image.title = title
        if is_public is not None:
            image.is_public = is_public

        image.save()

        serializer = ImageSerializer(image, context={'request': request})

        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, image_id):
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"code": 1, "message": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        # 只有图片的上传者可以删除该图片
        if image.user != request.user:
            raise PermissionDenied("You do not have permission to delete this image.")

        # # 删除图片文件（目前只实现了数据库的删除，七牛云上未删除）
        # delete_image_from_cloud(image.image_url)

        # 删除图片记录
        image.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

class ImageFeedView(ListAPIView):
    """信息流视图 - Instagram风格的图片流"""
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticated]

    # 自定义分页类
    class FeedPagination(PageNumberPagination):
        page_size = 20  # 每页显示20个图片
        page_size_query_param = 'page_size'
        max_page_size = 50

    pagination_class = FeedPagination

    def get_queryset(self):
        user = self.request.user
        
        # 获取当前用户关注的所有用户
        from community.models import Follow
        following_users = Follow.objects.filter(follower=user).values_list('following', flat=True)
        
        # 获取关注用户的公开图片 + 自己的所有图片
        queryset = Image.objects.filter(
            models.Q(user__in=following_users, is_public=True) |  # 关注用户的公开图片
            models.Q(user=user)  # 自己的所有图片
        ).select_related('user').prefetch_related('user__followers', 'user__following')
        
        # 按创建时间倒序排列
        return queryset.order_by('-created_at')

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def get_serializer_context(self):
        """为序列化器提供上下文"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

class ImageAIAnalysisView(APIView):
    """AI智能分析视图 - 获取图片的AI分析描述"""
    permission_classes = [IsAuthenticated]

    def get(self, request, image_id):
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"code": 1, "message": "Image not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            # 导入AI分析功能
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), 'ai'))
            from description import generate_image_description
            
            # 获取API密钥（建议从环境变量或配置文件中获取）
            api_key = "sk-ff8f03a8cfbc03d7df75b7ddb6b1fb7f0bfc8116e02986306865aa9149741301"
            
            # 调用AI分析
            result = generate_image_description(
                image_path=image.image_url,  # 使用图片URL
                api_key=api_key,
                model_id=3  # 使用模型ID 3
            )
            
            return Response({
                "code": 0,
                "message": "AI分析成功",
                "data": {
                    "description": result.get("description", "分析失败"),
                    "model_used": result.get("model_used", "未知模型"),
                    "image_id": image_id
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"AI分析失败: {str(e)}")
            return Response({
                "code": 1,
                "message": f"AI分析失败: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def ai_description_view(request, image_id):
    try:
        image = Image.objects.get(id=image_id)
    except Image.DoesNotExist:
        return Response({"error": "图片不存在"}, status=404)
    # 如果已分析过，直接返回
    if image.ai_description:
        return Response({"description": image.ai_description})
    api_key = "sk-ff8f03a8cfbc03d7df75b7ddb6b1fb7f0bfc8116e02986306865aa9149741301"
    import os
    import tempfile
    import requests
    # 下载图片到本地临时文件，分析后删除
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
        resp = requests.get(image.image_url)
        tmp.write(resp.content)
        tmp.flush()
        tmp_path = tmp.name
    try:
        result = generate_image_description(tmp_path, api_key, 3)
        result = result['description']
        image.ai_description = result
        image.save()
    finally:
        os.remove(tmp_path)
    return Response({"description": result})

class ImageTagsView(APIView):
    """图片标签管理视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, image_id):
        """获取图片的所有标签"""
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"error": "图片不存在"}, status=404)
        
        # 获取AI标签和用户标签
        ai_tags = image.get_tags_as_list()
        user_tags = image.user_tags or []
        
        return Response({
            "ai_tags": ai_tags,
            "user_tags": user_tags,
            "all_tags": list(set(ai_tags + user_tags))
        })
    
    def post(self, request, image_id):
        """添加用户自定义标签"""
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"error": "图片不存在"}, status=404)
        
        # 只有图片所有者可以编辑标签
        if image.user != request.user:
            return Response({"error": "无权限编辑此图片"}, status=403)
        
        new_tags = request.data.get('tags', [])
        if not isinstance(new_tags, list):
            return Response({"error": "标签必须是列表格式"}, status=400)
        
        # 合并现有标签和新标签，去重
        current_tags = image.user_tags or []
        updated_tags = list(set(current_tags + new_tags))
        image.user_tags = updated_tags
        image.save()
        
        return Response({
            "message": "标签添加成功",
            "user_tags": updated_tags
        })
    
    def delete(self, request, image_id):
        """删除用户自定义标签"""
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"error": "图片不存在"}, status=404)
        
        if image.user != request.user:
            return Response({"error": "无权限编辑此图片"}, status=403)
        
        tags_to_remove = request.data.get('tags', [])
        if not isinstance(tags_to_remove, list):
            return Response({"error": "标签必须是列表格式"}, status=400)
        
        current_tags = image.user_tags or []
        updated_tags = [tag for tag in current_tags if tag not in tags_to_remove]
        image.user_tags = updated_tags
        image.save()
        
        return Response({
            "message": "标签删除成功",
            "user_tags": updated_tags
        })


class ImageStyleAnalysisView(APIView):
    """AI风格分析视图"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, image_id):
        """执行AI风格分析"""
        try:
            image = Image.objects.get(id=image_id)
        except Image.DoesNotExist:
            return Response({"error": "图片不存在"}, status=404)
        
        # 如果已有分析结果，直接返回
        if image.ai_style_analysis:
            return Response({
                "style_analysis": image.ai_style_analysis,
                "emotion_analysis": image.ai_emotion_analysis
            })
        
        # 执行AI分析
        import tempfile
        import requests
        from .ai.style_analysis import analyze_image_style, analyze_image_emotion
        
        api_key = "sk-3658ae5ea3284ff4865227db05f4a214"
        
        # 下载图片到临时文件
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            resp = requests.get(image.image_url)
            tmp.write(resp.content)
            tmp.flush()
            tmp_path = tmp.name
        
        try:
            # 执行风格分析
            style_result = analyze_image_style(tmp_path, api_key)
            emotion_result = analyze_image_emotion(tmp_path, api_key)
            
            # 保存结果
            if style_result:
                image.ai_style_analysis = style_result
            if emotion_result:
                image.ai_emotion_analysis = emotion_result
            image.save()
            
            return Response({
                "style_analysis": style_result or {},
                "emotion_analysis": emotion_result or {}
            })
        finally:
            os.remove(tmp_path)


class ImageRecommendationView(APIView):
    """AI智能推荐视图"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """基于用户行为的智能推荐"""
        user = request.user
        
        # 获取用户最近交互的图片（点赞、评论、收藏）
        from community.models import Like, Comment, Favorite
        
        # 获取用户点赞的图片类别
        liked_images = Image.objects.filter(
            id__in=Like.objects.filter(
                user=user,
                like_type='image'
            ).values_list('object_id', flat=True)
        )
        
        # 统计类别偏好
        category_preferences = {}
        for img in liked_images:
            if img.category_id:
                category_preferences[img.category_id] = category_preferences.get(img.category_id, 0) + 1
        
        # 获取用户收藏的图片标签
        favorited_images = Image.objects.filter(favorited_by__user=user)
        tag_preferences = {}
        for img in favorited_images:
            for tag in img.get_tags_as_list():
                tag_preferences[tag] = tag_preferences.get(tag, 0) + 1
        
        # 基于偏好推荐
        recommended_images = Image.objects.filter(is_public=True).exclude(user=user)
        
        # 按类别推荐
        if category_preferences:
            top_categories = sorted(category_preferences.items(), key=lambda x: x[1], reverse=True)[:3]
            category_ids = [cat[0] for cat in top_categories]
            recommended_images = recommended_images.filter(category_id__in=category_ids)
        
        # 按标签推荐
        if tag_preferences:
            top_tags = sorted(tag_preferences.items(), key=lambda x: x[1], reverse=True)[:5]
            tag_names = [tag[0] for tag in top_tags]
            
            # 过滤包含这些标签的图片
            tag_filtered = []
            for img in recommended_images:
                if any(tag in img.get_tags_as_list() for tag in tag_names):
                    tag_filtered.append(img.id)
            
            if tag_filtered:
                recommended_images = recommended_images.filter(id__in=tag_filtered)
        
        # 限制数量并随机排序
        recommended_images = recommended_images.order_by('?')[:20]
        
        serializer = ImageSerializer(recommended_images, many=True, context={'request': request})
        
        return Response({
            "recommendations": serializer.data,
            "based_on": {
                "categories": list(category_preferences.keys())[:3],
                "tags": list(tag_preferences.keys())[:5]
            }
        })




class AIProcessView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, image_id):
        style = request.data.get('style')
        adjustments = request.data.get('adjustments', {})
        enhancements = request.data.get('enhancements', [])

        # 1. 获取图片对象和本地路径
        try:
            image_obj = Image.objects.get(id=image_id)
            image_url = image_obj.image_url  # 假设 image_url 是图片的可访问URL
        except Image.DoesNotExist:
            return Response({'error': '图片不存在'}, status=404)

        # 2. 下载图片到本地临时文件
        import requests
        resp = requests.get(image_url)
        if resp.status_code != 200:
            return Response({'error': '图片下载失败'}, status=500)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(resp.content)
            tmp.flush()
            input_path = tmp.name

        # 3. 处理图片
        from django.conf import settings
        import os, time, random
        processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
        os.makedirs(processed_dir, exist_ok=True)
        output_path = os.path.join(
            processed_dir,
            f'processed_{image_id}_{int(time.time()*1000)}_{random.randint(1000,9999)}.jpg'
        )
        img = PILImage.open(input_path)

        # 参数调节
        if any(adjustments):
            # 参数调节
            if 'brightness' in adjustments:
                try:
                    img = adjust_brightness(img, adjustments['brightness'])
                except Exception as e:
                    logger.error(f"亮度调节失败: {e}")
            if 'contrast' in adjustments:
                try:
                    img = adjust_contrast(img, adjustments['contrast'])
                except Exception as e:
                    logger.error(f"对比度调节失败: {e}")
            if 'saturation' in adjustments:
                try:
                    img = adjust_saturation(img, adjustments['saturation'])
                except Exception as e:
                    logger.error(f"饱和度调节失败: {e}")
            if 'hue' in adjustments:
                try:
                    img = adjust_hue(img, adjustments['hue'])
                except Exception as e:
                    logger.error(f"色调调节失败: {e}")
            if 'sharpness' in adjustments:
                try:
                    img = adjust_sharpness(img, adjustments['sharpness'])
                except Exception as e:
                    logger.error(f"锐化调节失败: {e}")
            if 'blur' in adjustments:
                try:
                    img = adjust_blur(img, adjustments['blur'])
                except Exception as e:
                    logger.error(f"模糊调节失败: {e}")
            img.save(output_path)
            img.close()
        else:
            # 没有参数调节，直接复制原图
            shutil.copy(input_path, output_path)

        # 智能增强
        if 'denoise' in enhancements:
            denoise_image(output_path, output_path, method="nlm")
        if 'upscale' in enhancements:
            super_resolution(output_path, output_path, scale=2)
        if 'color-enhance' in enhancements:
            color_enhance_image(output_path, output_path, factor=1.5)

        # 4. 直接返回media/processed目录下图片的URL
        # 清理临时文件
        os.remove(input_path)
        processed_url = request.build_absolute_uri(settings.MEDIA_URL + 'processed/' + os.path.basename(output_path))
        return Response({'processed_image_url': processed_url, 'file_name': os.path.basename(output_path)}, status=200)

# 新增：处理本地图片的接口
class AIProcessLocalView(APIView):
    """处理本地图片的AI视图"""
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            # 获取上传的图片文件
            image_file = request.FILES.get('image')
            if not image_file:
                return Response({'error': '请上传图片文件'}, status=400)
            
            # 获取处理参数
            params_str = request.data.get('params', '{}')
            try:
                params = json.loads(params_str)
            except json.JSONDecodeError:
                return Response({'error': '参数格式错误'}, status=400)
            
            adjustments = params.get('adjustments', {})
            enhancements = params.get('enhancements', [])
            
            # 保存上传的图片到临时文件
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                for chunk in image_file.chunks():
                    tmp.write(chunk)
                tmp.flush()
                input_path = tmp.name
            
            # 处理图片
            from django.conf import settings
            import os, time, random
            processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
            os.makedirs(processed_dir, exist_ok=True)
            output_path = os.path.join(
                processed_dir,
                f'processed_local_{int(time.time()*1000)}_{random.randint(1000,9999)}.jpg'
            )
            
            img = PILImage.open(input_path)
            
            # 参数调节
            if any(adjustments):
                if 'brightness' in adjustments:
                    try:
                        img = adjust_brightness(img, adjustments['brightness'])
                    except Exception as e:
                        logger.error(f"亮度调节失败: {e}")
                if 'contrast' in adjustments:
                    try:
                        img = adjust_contrast(img, adjustments['contrast'])
                    except Exception as e:
                        logger.error(f"对比度调节失败: {e}")
                if 'saturation' in adjustments:
                    try:
                        img = adjust_saturation(img, adjustments['saturation'])
                    except Exception as e:
                        logger.error(f"饱和度调节失败: {e}")
                if 'hue' in adjustments:
                    try:
                        img = adjust_hue(img, adjustments['hue'])
                    except Exception as e:
                        logger.error(f"色调调节失败: {e}")
                if 'sharpness' in adjustments:
                    try:
                        img = adjust_sharpness(img, adjustments['sharpness'])
                    except Exception as e:
                        logger.error(f"锐化调节失败: {e}")
                if 'blur' in adjustments:
                    try:
                        img = adjust_blur(img, adjustments['blur'])
                    except Exception as e:
                        logger.error(f"模糊调节失败: {e}")
                img.save(output_path)
                img.close()
            else:
                # 没有参数调节，直接复制原图
                shutil.copy(input_path, output_path)
            
            # 智能增强
            if 'denoise' in enhancements:
                denoise_image(output_path, output_path, method="nlm")
            if 'upscale' in enhancements:
                super_resolution(output_path, output_path, scale=2)
            if 'color-enhance' in enhancements:
                color_enhance_image(output_path, output_path, factor=1.5)
            
            # 清理临时文件
            os.remove(input_path)
            
            # 返回处理后的图片URL
            processed_url = request.build_absolute_uri(settings.MEDIA_URL + 'processed/' + os.path.basename(output_path))
            logger.info(f"返回处理后的图片URL: {processed_url}")
            logger.info(f"文件路径: {output_path}")
            logger.info(f"文件是否存在: {os.path.exists(output_path)}")
            return Response({
                'processed_image_url': processed_url, 
                'file_name': os.path.basename(output_path)
            }, status=200)
            
        except Exception as e:
            logger.error(f"本地图片处理失败: {e}")
            return Response({'error': '图片处理失败'}, status=500)

# 新增：删除处理后图片的接口
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

class DeleteProcessedImageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        file_name = request.data.get('file_name')
        if not file_name:
            return Response({'error': 'file_name required'}, status=status.HTTP_400_BAD_REQUEST)
        processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
        file_path = os.path.join(processed_dir, file_name)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                return Response({'message': 'deleted'}, status=200)
            except Exception as e:
                return Response({'error': str(e)}, status=500)
        else:
            return Response({'error': 'file not found'}, status=404)
