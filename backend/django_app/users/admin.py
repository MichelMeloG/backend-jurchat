from django.contrib import admin
from .models import User, UserPlanHistory


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'username', 'plan', 'documents_uploaded_this_month', 'ai_tokens_used_this_month', 'is_active']
    list_filter = ['plan', 'is_active', 'created_at']
    search_fields = ['email', 'username']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserPlanHistory)
class UserPlanHistoryAdmin(admin.ModelAdmin):
    list_display = ['user', 'old_plan', 'new_plan', 'changed_at', 'reason']
    list_filter = ['old_plan', 'new_plan', 'changed_at']
    search_fields = ['user__email', 'reason']
