from django.urls import path
from .views import (
    DocumentUploadView,
    DocumentListView,
    DocumentDetailView,
    DocumentShareView,
    SharedDocumentsView,
    reprocess_document
)

urlpatterns = [
    path('upload/', DocumentUploadView.as_view(), name='document_upload'),
    path('', DocumentListView.as_view(), name='document_list'),
    path('<uuid:pk>/', DocumentDetailView.as_view(), name='document_detail'),
    path('<uuid:document_id>/reprocess/', reprocess_document, name='document_reprocess'),
    path('share/', DocumentShareView.as_view(), name='document_share'),
    path('shared/', SharedDocumentsView.as_view(), name='shared_documents'),
]
