import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'image_repo_backend.settings')
django.setup()

from tags.models import Tag

# 先清空所有标签
Tag.objects.all().delete()
print("已清空所有标签！")

txt_path = os.path.join(os.path.dirname(__file__), 'images', 'ai', 'initial_tags.txt')

with open(txt_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if ':' in line:
            tag_id, name = line.split(':', 1)
            tag_id = int(tag_id.strip())
            name = name.strip()
            Tag.objects.create(id=tag_id, name=name)
            print(f"标签 {name} 导入成功")

print("标签批量导入完成！")