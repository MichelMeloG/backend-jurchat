from django.urls import path
from .views import RegisterView, LoginView, ProfileView, PlanView, upgrade_plan

urlpatterns = [
    # Authentication endpoints
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # User profile endpoints
    path('profile/', ProfileView.as_view(), name='profile'),
    path('plan/', PlanView.as_view(), name='plan'),
    path('plan/upgrade/', upgrade_plan, name='upgrade_plan'),
]
