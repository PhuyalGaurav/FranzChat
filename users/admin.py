from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, FriendRequest


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {
            'fields': (
                'bio', 'avatar', 'date_of_birth',
                'created_at', 'updated_at', 'friends'
            )
        }),
    )
    list_display = (
        'username', 'email', 'first_name', 'last_name',
        'is_staff', 'is_active', 'date_of_birth'
    )
    readonly_fields = ('created_at', 'updated_at')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(FriendRequest)
