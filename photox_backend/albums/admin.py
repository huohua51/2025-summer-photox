from django.contrib import admin
from .models import Album
from images.models import Image

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'is_public', 'image_count', 'created_at']
    list_filter = ['is_public', 'created_at', 'user']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at']
    filter_horizontal = ['images']  # 使用水平过滤器方便选择图片
    
    def image_count(self, obj):
        return obj.images.count()
    image_count.short_description = '图片数量'
    
    fieldsets = (
        ('基本信息', {
            'fields': ('title', 'description', 'user', 'is_public')
        }),
        ('图片管理', {
            'fields': ('images',),
        }),
        ('时间信息', {
            'fields': ('created_at',),
        }),
    )
