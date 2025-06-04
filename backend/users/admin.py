from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.safestring import mark_safe

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Админ-панель для пользователей."""
    
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'get_avatar_preview', 'is_staff', 'date_joined'
    )
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login', 'get_avatar_preview')
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Дополнительные поля', {
            'fields': ('avatar', 'get_avatar_preview')
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Дополнительная информация', {
            'fields': ('first_name', 'last_name', 'email', 'avatar')
        }),
    )
    
    def get_avatar_preview(self, obj):
        """Превью аватара."""
        if obj.avatar:
            return mark_safe(
                f'<img src="{obj.avatar.url}" style="max-height: 100px; max-width: 100px; border-radius: 50%;">'
            )
        return 'Нет аватара'
    get_avatar_preview.short_description = 'Превью аватара'
