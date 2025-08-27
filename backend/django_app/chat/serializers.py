from rest_framework import serializers
from .models import ChatSession, ChatMessage, ChatFeedback, ChatTemplate


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages"""
    
    class Meta:
        model = ChatMessage
        fields = ('id', 'role', 'content', 'tokens_used', 'metadata', 'created_at')
        read_only_fields = ('id', 'tokens_used', 'created_at')


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions"""
    
    messages = ChatMessageSerializer(many=True, read_only=True)
    message_count = serializers.SerializerMethodField()
    can_send_message = serializers.SerializerMethodField()
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = (
            'id', 'document', 'document_title', 'title', 'is_active',
            'messages', 'message_count', 'can_send_message',
            'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    def get_message_count(self, obj):
        return obj.get_message_count()
    
    def get_can_send_message(self, obj):
        return obj.can_send_message()


class ChatSessionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for chat session listing"""
    
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    document_title = serializers.CharField(source='document.title', read_only=True)
    
    class Meta:
        model = ChatSession
        fields = (
            'id', 'document', 'document_title', 'title', 'is_active',
            'message_count', 'last_message', 'created_at', 'updated_at'
        )
    
    def get_message_count(self, obj):
        return obj.get_message_count()
    
    def get_last_message(self, obj):
        last_message = obj.messages.last()
        if last_message:
            return {
                'content': last_message.content[:100] + '...' if len(last_message.content) > 100 else last_message.content,
                'role': last_message.role,
                'created_at': last_message.created_at
            }
        return None


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending chat messages"""
    
    message = serializers.CharField(max_length=2000)
    
    def validate_message(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty")
        return value.strip()


class ChatFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for chat feedback"""
    
    class Meta:
        model = ChatFeedback
        fields = ('message', 'rating', 'comment', 'created_at')
        read_only_fields = ('created_at',)


class ChatTemplateSerializer(serializers.ModelSerializer):
    """Serializer for chat templates"""
    
    class Meta:
        model = ChatTemplate
        fields = (
            'id', 'title', 'category', 'template', 'description',
            'usage_count', 'created_at'
        )
        read_only_fields = ('id', 'usage_count', 'created_at')


class ChatExportSerializer(serializers.Serializer):
    """Serializer for chat export requests"""
    
    format = serializers.ChoiceField(choices=['PDF', 'DOCX', 'TXT'])
    include_metadata = serializers.BooleanField(default=False)
