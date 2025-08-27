import uuid
from django.db import models
from django.conf import settings


class ChatSession(models.Model):
    """Chat session for a specific document"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    document = models.ForeignKey('documents.Document', on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(max_length=255, help_text='Chat session title')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'chat_sessions'
        ordering = ['-updated_at']
        unique_together = ['user', 'document']
    
    def __str__(self):
        return f"Chat: {self.title} ({self.user.email})"
    
    def get_message_count(self):
        """Get total message count for this session"""
        return self.messages.count()
    
    def can_send_message(self):
        """Check if user can send more messages based on plan limits"""
        from django.conf import settings
        
        limit = settings.PLAN_LIMITS[self.user.plan]['chat_messages_per_document']
        if limit == -1:  # Unlimited
            return True
        
        return self.get_message_count() < limit


class ChatMessage(models.Model):
    """Individual chat message"""
    
    ROLE_CHOICES = [
        ('USER', 'User'),
        ('ASSISTANT', 'Assistant'),
        ('SYSTEM', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens_used = models.IntegerField(default=0, help_text='AI tokens used for this message')
    metadata = models.JSONField(default=dict, help_text='Additional metadata for the message')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_messages'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}..."


class ChatFeedback(models.Model):
    """User feedback on chat responses"""
    
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_feedback'
    
    def __str__(self):
        return f"Feedback for {self.message.id}: {self.rating}/5"


class ChatTemplate(models.Model):
    """Predefined chat templates for common legal questions"""
    
    CATEGORY_CHOICES = [
        ('CONTRACT', 'Contract Analysis'),
        ('LAWSUIT', 'Lawsuit Questions'),
        ('REGULATION', 'Regulation Interpretation'),
        ('GENERAL', 'General Legal Questions'),
    ]
    
    title = models.CharField(max_length=255)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    template = models.TextField(help_text='Template with placeholders like {document_type}')
    description = models.TextField(help_text='Description of when to use this template')
    is_active = models.BooleanField(default=True)
    usage_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'chat_templates'
        ordering = ['category', 'title']
    
    def __str__(self):
        return f"{self.category}: {self.title}"
    
    def increment_usage(self):
        """Increment usage count"""
        self.usage_count += 1
        self.save()


class ChatExport(models.Model):
    """Export chat sessions to different formats"""
    
    FORMAT_CHOICES = [
        ('PDF', 'PDF'),
        ('DOCX', 'Word Document'),
        ('TXT', 'Text File'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='exports')
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    file = models.FileField(upload_to='chat_exports/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'chat_exports'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Export {self.session.title} to {self.format}"
