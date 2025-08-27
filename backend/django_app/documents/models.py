import os
import uuid
from django.db import models
from django.conf import settings
from cryptography.fernet import Fernet


def document_upload_path(instance, filename):
    """Generate upload path for document files"""
    # Create a unique filename to prevent conflicts
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return os.path.join('documents', str(instance.user.id), filename)


class Document(models.Model):
    """Document model for storing uploaded legal documents"""
    
    STATUS_CHOICES = [
        ('UPLOADED', 'Uploaded'),
        ('PROCESSING', 'Processing'),
        ('PROCESSED', 'Processed'),
        ('ERROR', 'Error'),
    ]
    
    TYPE_CHOICES = [
        ('CONTRACT', 'Contract'),
        ('LAWSUIT', 'Lawsuit'),
        ('REGULATION', 'Regulation'),
        ('DECISION', 'Legal Decision'),
        ('OTHER', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    document_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='OTHER')
    file = models.FileField(upload_to=document_upload_path)
    file_size = models.BigIntegerField(help_text='File size in bytes')
    mime_type = models.CharField(max_length=100)
    
    # Processing information
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UPLOADED')
    extracted_text = models.TextField(blank=True, help_text='Extracted text from document')
    summary = models.TextField(blank=True, help_text='AI-generated summary in plain language')
    summary_tokens = models.IntegerField(default=0, help_text='Tokens used for summary generation')
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'documents'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.user.email})"
    
    def encrypt_sensitive_data(self, data):
        """Encrypt sensitive data using AES-256"""
        key = settings.ENCRYPTION_KEY.encode()
        fernet = Fernet(key)
        return fernet.encrypt(data.encode()).decode()
    
    def decrypt_sensitive_data(self, encrypted_data):
        """Decrypt sensitive data"""
        key = settings.ENCRYPTION_KEY.encode()
        fernet = Fernet(key)
        return fernet.decrypt(encrypted_data.encode()).decode()
    
    def get_file_extension(self):
        """Get file extension"""
        return os.path.splitext(self.file.name)[1].lower()
    
    def is_supported_format(self):
        """Check if file format is supported"""
        supported_formats = ['.pdf', '.doc', '.docx', '.txt']
        return self.get_file_extension() in supported_formats


class DocumentProcessingLog(models.Model):
    """Log processing steps for documents"""
    
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='processing_logs')
    step = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[
        ('STARTED', 'Started'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    ])
    message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_processing_logs'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.document.title} - {self.step}: {self.status}"


class DocumentShare(models.Model):
    """Model for sharing documents between users"""
    
    PERMISSION_CHOICES = [
        ('READ', 'Read Only'),
        ('COMMENT', 'Read and Comment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='shares')
    shared_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='shared_documents')
    shared_with = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_documents')
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES, default='READ')
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_shares'
        unique_together = ['document', 'shared_with']
    
    def __str__(self):
        return f"{self.document.title} shared with {self.shared_with.email}"
