import requests
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone
from documents.models import Document
from .models import ChatSession, ChatMessage, ChatFeedback, ChatTemplate
from .serializers import (
    ChatSessionSerializer,
    ChatSessionListSerializer,
    SendMessageSerializer,
    ChatFeedbackSerializer,
    ChatTemplateSerializer,
    ChatExportSerializer
)


class ChatSessionListCreateView(generics.ListCreateAPIView):
    """List and create chat sessions"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ChatSessionListSerializer
        return ChatSessionSerializer
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        document_id = request.data.get('document')
        
        # Check if document exists and belongs to user
        document = get_object_or_404(Document, id=document_id, user=request.user)
        
        # Check if document is processed
        if document.status != 'PROCESSED':
            return Response({
                'error': 'Document must be processed before starting a chat'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if chat session already exists for this document
        existing_session = ChatSession.objects.filter(
            user=request.user,
            document=document
        ).first()
        
        if existing_session:
            return Response({
                'message': 'Chat session already exists for this document',
                'session': ChatSessionSerializer(existing_session, context={'request': request}).data
            }, status=status.HTTP_200_OK)
        
        # Create new chat session
        session = ChatSession.objects.create(
            user=request.user,
            document=document,
            title=f"Chat sobre {document.title}"
        )
        
        # Create welcome message
        welcome_message = f"Olá! Estou aqui para ajudar você a entender o documento '{document.title}'. Você pode me fazer perguntas sobre o conteúdo, pedir esclarecimentos ou solicitar análises específicas. Como posso ajudá-lo?"
        
        ChatMessage.objects.create(
            session=session,
            role='ASSISTANT',
            content=welcome_message
        )
        
        return Response({
            'message': 'Chat session created successfully',
            'session': ChatSessionSerializer(session, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class ChatSessionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Chat session detail, update, and delete"""
    
    serializer_class = ChatSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_message(request, session_id):
    """Send a message in a chat session"""
    
    # Get chat session
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return Response({
            'error': 'Chat session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Check if user can send more messages
    if not session.can_send_message():
        return Response({
            'error': 'Message limit reached for your plan'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Validate message
    serializer = SendMessageSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    user_message_content = serializer.validated_data['message']
    
    # Estimate tokens needed
    estimated_tokens = len(user_message_content.split()) * 2  # Rough estimation
    
    # Check AI tokens limit
    if not request.user.can_use_ai_tokens(estimated_tokens):
        return Response({
            'error': 'AI token limit reached for your plan'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Create user message
    user_message = ChatMessage.objects.create(
        session=session,
        role='USER',
        content=user_message_content
    )
    
    try:
        # Send to FastAPI service for AI response
        fastapi_url = f"{settings.FASTAPI_SERVICE_URL}/ai/chat"
        
        # Prepare conversation context
        recent_messages = session.messages.order_by('-created_at')[:10]  # Last 10 messages
        conversation_history = []
        
        for msg in reversed(recent_messages):
            conversation_history.append({
                'role': msg.role.lower(),
                'content': msg.content
            })
        
        payload = {
            'message': user_message_content,
            'document_id': str(session.document.id),
            'document_content': session.document.extracted_text,
            'document_summary': session.document.summary,
            'conversation_history': conversation_history
        }
        
        response = requests.post(
            fastapi_url,
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Create assistant message
            assistant_message = ChatMessage.objects.create(
                session=session,
                role='ASSISTANT',
                content=result['response'],
                tokens_used=result.get('tokens_used', 0),
                metadata=result.get('metadata', {})
            )
            
            # Update user AI token usage
            request.user.use_ai_tokens(result.get('tokens_used', 0))
            
            # Update session timestamp
            session.updated_at = timezone.now()
            session.save()
            
            return Response({
                'user_message': {
                    'id': str(user_message.id),
                    'content': user_message.content,
                    'created_at': user_message.created_at
                },
                'assistant_message': {
                    'id': str(assistant_message.id),
                    'content': assistant_message.content,
                    'tokens_used': assistant_message.tokens_used,
                    'created_at': assistant_message.created_at
                }
            }, status=status.HTTP_200_OK)
        
        else:
            # If AI service fails, still keep the user message but add error response
            error_message = ChatMessage.objects.create(
                session=session,
                role='SYSTEM',
                content='Desculpe, houve um erro temporário no serviço de IA. Tente novamente em alguns instantes.'
            )
            
            return Response({
                'user_message': {
                    'id': str(user_message.id),
                    'content': user_message.content,
                    'created_at': user_message.created_at
                },
                'error_message': {
                    'id': str(error_message.id),
                    'content': error_message.content,
                    'created_at': error_message.created_at
                }
            }, status=status.HTTP_200_OK)
            
    except Exception as e:
        # Create error message
        error_message = ChatMessage.objects.create(
            session=session,
            role='SYSTEM',
            content=f'Erro interno: {str(e)}'
        )
        
        return Response({
            'user_message': {
                'id': str(user_message.id),
                'content': user_message.content,
                'created_at': user_message.created_at
            },
            'error_message': {
                'id': str(error_message.id),
                'content': error_message.content,
                'created_at': error_message.created_at
            }
        }, status=status.HTTP_200_OK)


class ChatFeedbackView(generics.CreateAPIView):
    """Submit feedback for chat messages"""
    
    serializer_class = ChatFeedbackSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        message_id = request.data.get('message')
        
        # Verify message belongs to user
        try:
            message = ChatMessage.objects.get(
                id=message_id,
                session__user=request.user,
                role='ASSISTANT'  # Only allow feedback on assistant messages
            )
        except ChatMessage.DoesNotExist:
            return Response({
                'error': 'Message not found or not eligible for feedback'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if feedback already exists
        if hasattr(message, 'feedback'):
            return Response({
                'error': 'Feedback already provided for this message'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return super().create(request, *args, **kwargs)


class ChatTemplateView(generics.ListAPIView):
    """List available chat templates"""
    
    serializer_class = ChatTemplateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return ChatTemplate.objects.filter(is_active=True)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def export_chat(request, session_id):
    """Export chat session to file"""
    
    # Get chat session
    try:
        session = ChatSession.objects.get(id=session_id, user=request.user)
    except ChatSession.DoesNotExist:
        return Response({
            'error': 'Chat session not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ChatExportSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    # In a real implementation, this would be handled by a background task
    # For now, just return a success message
    return Response({
        'message': 'Export request received. You will receive the file via email when ready.',
        'format': serializer.validated_data['format']
    }, status=status.HTTP_202_ACCEPTED)
