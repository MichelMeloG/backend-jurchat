from rest_framework import serializers
from .models import Document, DocumentShare, DocumentProcessingLog


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Serializer for document upload"""
    
    class Meta:
        model = Document
        fields = ('title', 'description', 'document_type', 'file')
    
    def validate_file(self, value):
        """Validate uploaded file"""
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024  # 50MB
        if value.size > max_size:
            raise serializers.ValidationError("File size cannot exceed 50MB")
        
        # Check file extension
        allowed_extensions = ['.pdf', '.doc', '.docx', '.txt']
        file_extension = value.name.split('.')[-1].lower()
        if f'.{file_extension}' not in allowed_extensions:
            raise serializers.ValidationError(
                f"File type not supported. Allowed types: {', '.join(allowed_extensions)}"
            )
        
        return value


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for document details"""
    
    file_url = serializers.SerializerMethodField()
    processing_logs = serializers.SerializerMethodField()
    
    class Meta:
        model = Document
        fields = (
            'id', 'title', 'description', 'document_type', 'file_url',
            'file_size', 'mime_type', 'status', 'summary', 'summary_tokens',
            'created_at', 'updated_at', 'processed_at', 'processing_logs'
        )
        read_only_fields = (
            'id', 'file_url', 'file_size', 'mime_type', 'status', 'summary',
            'summary_tokens', 'created_at', 'updated_at', 'processed_at'
        )
    
    def get_file_url(self, obj):
        """Get file URL"""
        request = self.context.get('request')
        if obj.file and request:
            return request.build_absolute_uri(obj.file.url)
        return None
    
    def get_processing_logs(self, obj):
        """Get processing logs"""
        logs = obj.processing_logs.all()[:5]  # Last 5 logs
        return DocumentProcessingLogSerializer(logs, many=True).data


class DocumentListSerializer(serializers.ModelSerializer):
    """Simplified serializer for document listing"""
    
    class Meta:
        model = Document
        fields = (
            'id', 'title', 'document_type', 'status', 'file_size',
            'created_at', 'processed_at'
        )


class DocumentProcessingLogSerializer(serializers.ModelSerializer):
    """Serializer for processing logs"""
    
    class Meta:
        model = DocumentProcessingLog
        fields = ('step', 'status', 'message', 'created_at')


class DocumentShareSerializer(serializers.ModelSerializer):
    """Serializer for document sharing"""
    
    shared_with_email = serializers.EmailField(write_only=True)
    shared_with = serializers.StringRelatedField(read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = DocumentShare
        fields = (
            'id', 'document', 'document_title', 'shared_with_email', 
            'shared_with', 'permission', 'expires_at', 'created_at'
        )
        read_only_fields = ('id', 'shared_with', 'created_at')
    
    def create(self, validated_data):
        from django.contrib.auth import get_user_model
        
        User = get_user_model()
        shared_with_email = validated_data.pop('shared_with_email')
        
        try:
            shared_with = User.objects.get(email=shared_with_email)
        except User.DoesNotExist:
            raise serializers.ValidationError({
                'shared_with_email': 'User with this email does not exist'
            })
        
        validated_data['shared_with'] = shared_with
        validated_data['shared_by'] = self.context['request'].user
        
        return super().create(validated_data)
