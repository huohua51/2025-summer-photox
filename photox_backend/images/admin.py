# images/admin.py
from django.contrib import admin
from .models import Image  # ✅ 这是你定义的模型

@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at', 'is_public')
    search_fields = ('title', 'tags')
    list_filter = ('is_public', 'created_at')
