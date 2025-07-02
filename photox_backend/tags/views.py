from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAdminUser
import logging

from tags.models import Tag
from tags.serializers import TagSerializer, TagImportSerializer

logger = logging.getLogger(__name__)


class TagListCreateView(generics.ListCreateAPIView):
    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None  # 禁用分页

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        if not name:
            return Response({"error": "标签名称不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        # 生成ID - 获取当前最大ID+1
        max_id = Tag.objects.all().order_by('-id').first()
        new_id = max_id.id + 1 if max_id else 1

        # 简化创建逻辑
        tag = Tag.objects.create(id=new_id, name=name)
        serializer = self.get_serializer(tag)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TagDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]
    lookup_field = 'id'


class TagImportView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        serializer = TagImportSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        file = request.FILES['file']
        content = file.read().decode('utf-8').splitlines()
        created_count = 0
        updated_count = 0

        for line in content:
            line = line.strip()
            if not line or ':' not in line:
                continue

            try:
                parts = line.split(':', 1)
                tag_id = int(parts[0].strip())
                tag_name = parts[1].strip()

                # 创建或更新标签（不再处理时间字段）
                tag, created = Tag.objects.update_or_create(
                    id=tag_id,
                    defaults={'name': tag_name}
                )

                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except (ValueError, TypeError) as e:
                logger.error(f"解析标签行错误: {line} - {str(e)}")
                continue

        return Response({
            "code": 0,
            "message": "标签导入成功",
            "data": {
                "total_lines": len(content),
                "created": created_count,
                "updated": updated_count
            }
        }, status=status.HTTP_200_OK)