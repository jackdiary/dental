from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'username', 'is_premium', 'is_staff', 'created_at')
    list_filter = ('is_premium', 'is_staff', 'is_superuser', 'created_at')
    search_fields = ('email', 'username', 'phone')
    ordering = ('-created_at',)
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('추가 정보', {
            'fields': ('phone', 'preferred_district', 'is_premium', 'notification_enabled')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('추가 정보', {
            'fields': ('email', 'phone', 'preferred_district')
        }),
    )