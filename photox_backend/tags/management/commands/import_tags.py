from django.core.management.base import BaseCommand
from tags.models import Tag
import os


class Command(BaseCommand):
    help = '从文件导入初始标签数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='包含标签数据的文件路径',
            default=None
        )

    def handle(self, *args, **options):
        file_path = options['file']

        if not file_path:
            self.stdout.write(self.style.ERROR("请使用 --file 参数指定文件路径"))
            return

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f"文件不存在: {file_path}"))
            return

        if file_path.endswith('.txt'):
            self.import_from_txt(file_path)
        else:
            self.stdout.write(self.style.ERROR("只支持.txt格式文件"))

    def import_from_txt(self, file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total = len(lines)
            created = 0
            updated = 0

            for line in lines:
                line = line.strip()
                if not line or ':' not in line:
                    continue

                try:
                    parts = line.split(':', 1)
                    tag_id = int(parts[0].strip())
                    tag_name = parts[1].strip()

                    _, created_flag = Tag.objects.update_or_create(
                        id=tag_id,
                        defaults={'name': tag_name}
                    )

                    if created_flag:
                        created += 1
                    else:
                        updated += 1

                except (ValueError, TypeError) as e:
                    self.stdout.write(self.style.ERROR(f"解析错误: {line} - {str(e)}"))

        self.stdout.write(self.style.SUCCESS(
            f"标签导入完成! 总数: {total}, 新增: {created}, 更新: {updated}"
        ))