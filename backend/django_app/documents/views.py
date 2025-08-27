import os
import requests
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.conf import settings
from django.utils import timezone
from .models import Document, DocumentShare, DocumentProcessingLog
from .serializers import (
    DocumentUploadSerializer,
    DocumentSerializer,
    DocumentListSerializer,
    DocumentShareSerializer
)


class DocumentUploadView(generics.CreateAPIView):
    """Document upload endpoint"""
    
    serializer_class = DocumentUploadSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def create(self, request, *args, **kwargs):
        # Check if user can upload documents
        user = request.user
        if not user.can_upload_document():
            return Response({
                'error': 'Document upload limit reached for your plan'
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create document instance
        document = serializer.save(
            user=user,
            file_size=request.FILES['file'].size,
            mime_type=request.FILES['file'].content_type
        )
        
        # Increment user document count
        user.increment_document_count()
        
        # Create processing log
        DocumentProcessingLog.objects.create(
            document=document,
            step='UPLOAD',
            status='COMPLETED',
            message='Document uploaded successfully'
        )
        
        # Start processing (async)
        self.start_document_processing(document)
        
        return Response({
            'message': 'Document uploaded successfully',
            'document': DocumentSerializer(document, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)
    
    def start_document_processing(self, document):
        """Start document processing with FastAPI service"""
        try:
            # Update status to processing
            document.status = 'PROCESSING'
            document.save()
            
            DocumentProcessingLog.objects.create(
                document=document,
                step='PROCESSING_START',
                status='STARTED',
                message='Starting document processing'
            )
            
            # Send to FastAPI service for processing
            fastapi_url = f"{settings.FASTAPI_SERVICE_URL}/ai/summarize"
            
            # In a real implementation, this should be done asynchronously
            # using Celery or similar task queue
            with open(document.file.path, 'rb') as f:
                files = {'file': f}
                data = {
                    'document_id': str(document.id),
                    'user_id': document.user.id
                }
                
                response = requests.post(
                    fastapi_url,
                    files=files,
                    data=data,
                    timeout=300  # 5 minutes timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    # Update document with processing results
                    document.extracted_text = result.get('extracted_text', '')
                    document.summary = result.get('summary', '')
                    document.summary_tokens = result.get('tokens_used', 0)
                    document.status = 'PROCESSED'
                    document.processed_at = timezone.now()
                    document.save()
                    
                    # Update user AI token usage
                    document.user.use_ai_tokens(document.summary_tokens)
                    
                    DocumentProcessingLog.objects.create(
                        document=document,
                        step='PROCESSING_COMPLETE',
                        status='COMPLETED',
                        message='Document processed successfully'
                    )
                else:
                    raise Exception(f"FastAPI service error: {response.status_code}")
                    
        except Exception as e:
            document.status = 'ERROR'
            document.save()
            
            DocumentProcessingLog.objects.create(
                document=document,
                step='PROCESSING_ERROR',
                status='FAILED',
                message=f'Processing failed: {str(e)}'
            )


class DocumentListView(generics.ListAPIView):
    """List user's documents"""
    
    serializer_class = DocumentListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)


class DocumentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Document detail, update, and delete"""
    
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(user=self.request.user)


class DocumentShareView(generics.CreateAPIView):
    """Share document with another user"""
    
    serializer_class = DocumentShareSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return DocumentShare.objects.filter(shared_by=self.request.user)


class SharedDocumentsView(generics.ListAPIView):
    """List documents shared with current user"""
    
    serializer_class = DocumentListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        shared_docs = DocumentShare.objects.filter(
            shared_with=self.request.user
        ).values_list('document_id', flat=True)
        
        return Document.objects.filter(id__in=shared_docs)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def reprocess_document(request, document_id):
    """Reprocess a document"""
    try:
        document = Document.objects.get(id=document_id, user=request.user)
    except Document.DoesNotExist:
        return Response({
            'error': 'Document not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if document.status == 'PROCESSING':
        return Response({
            'error': 'Document is already being processed'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Check AI tokens limit
    estimated_tokens = 1000  # Estimated tokens for reprocessing
    if not request.user.can_use_ai_tokens(estimated_tokens):
        return Response({
            'error': 'AI token limit reached for your plan'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Start reprocessing
    upload_view = DocumentUploadView()
    upload_view.start_document_processing(document)
    
    return Response({
        'message': 'Document reprocessing started'
    }, status=status.HTTP_200_OK)
