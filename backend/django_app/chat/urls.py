from django.urls import path
from .views import (
    ChatSessionListCreateView,
    ChatSessionDetailView,
    send_message,
    ChatFeedbackView,
    ChatTemplateView,
    export_chat
)

urlpatterns = [
    path('sessions/', ChatSessionListCreateView.as_view(), name='chat_sessions'),
    path('sessions/<uuid:pk>/', ChatSessionDetailView.as_view(), name='chat_session_detail'),
    path('<uuid:session_id>/send/', send_message, name='send_message'),
    path('feedback/', ChatFeedbackView.as_view(), name='chat_feedback'),
    path('templates/', ChatTemplateView.as_view(), name='chat_templates'),
    path('<uuid:session_id>/export/', export_chat, name='export_chat'),
]
