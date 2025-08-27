from django.contrib import admin
from .models import Document, DocumentShare, DocumentProcessingLog


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'document_type', 'status', 'file_size', 'created_at']
    list_filter = ['status', 'document_type', 'created_at']
    search_fields = ['title', 'user__email']
    readonly_fields = ['id', 'created_at', 'updated_at', 'processed_at']


@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    list_display = ['document', 'shared_by', 'shared_with', 'permission', 'created_at']
    list_filter = ['permission', 'created_at']
    search_fields = ['document__title', 'shared_by__email', 'shared_with__email']


@admin.register(DocumentProcessingLog)
class DocumentProcessingLogAdmin(admin.ModelAdmin):
    list_display = ['document', 'step', 'status', 'created_at']
    list_filter = ['status', 'step', 'created_at']
    search_fields = ['document__title']
