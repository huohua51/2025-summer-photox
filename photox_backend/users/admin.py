from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser

# 自定义用户管理界面
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # 列表页显示的字段
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined')
    
    # 列表页可以直接编辑的字段
    list_editable = ('is_active',)
    
    # 右侧过滤器
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups', 'date_joined')
    
    # 搜索字段
    search_fields = ('username', 'first_name', 'last_name', 'email')
    
    # 排序
    ordering = ('-date_joined',)
    
    # 分组显示字段
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('个人信息', {'fields': ('first_name', 'last_name', 'email', 'avatar', 'bio')}),
        ('权限', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('重要日期', {'fields': ('last_login', 'date_joined')}),
    )
    
    # 添加用户时的字段
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2'),
        }),
    )

# 自定义站点标题
admin.site.site_header = "Photox 管理后台"
admin.site.site_title = "Photox Admin"
admin.site.index_title = "欢迎使用 Photox 管理后台"

# 如果你想自定义组管理界面
admin.site.unregister(Group)
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_users_count')
    search_fields = ('name',)
    
    def get_users_count(self, obj):
        return obj.user_set.count()
    get_users_count.short_description = '用户数量'
