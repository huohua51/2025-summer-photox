from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from .models import CustomUser

# 自定义用户管理界面
class CustomUserAdmin(UserAdmin):
    list_per_page = 10
    # 可根据需要自定义list_display等
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'is_active', 'is_verified', 'role')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'is_verified', 'role')

admin.site.register(CustomUser, CustomUserAdmin)

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
