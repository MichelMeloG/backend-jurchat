"""URL Configuration for JurChat"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_root(request):
    """API root endpoint with available routes"""
    return JsonResponse({
        'message': 'JurChat Backend API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'admin': '/admin/',
            'auth': {
                'register': '/api/auth/register/',
                'login': '/api/auth/login/',
            },
            'user': {
                'profile': '/api/user/profile/',
                'plan': '/api/user/plan/',
            },
            'documents': {
                'upload': '/api/documents/upload/',
                'list': '/api/documents/',
            },
            'chat': {
                'sessions': '/api/chat/sessions/',
            },
            'api_docs': '/api/docs/' if settings.DEBUG else None,
        },
        'documentation': '/admin/' if settings.DEBUG else None,
    })


urlpatterns = [
    path('', api_root, name='api_root'),
    path('admin/', admin.site.urls),
    path('api/auth/', include('users.urls')),
    path('api/user/', include('users.urls')),
    path('api/documents/', include('documents.urls')),
    path('api/chat/', include('chat.urls')),
    path('api/', api_root, name='api_root_alt'),  # Alternative API root
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
