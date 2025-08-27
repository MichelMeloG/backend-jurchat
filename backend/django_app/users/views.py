from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import User
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer,
    UserPlanSerializer
)


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'User created successfully',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(generics.GenericAPIView):
    """User login endpoint"""
    
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        return Response({
            'message': 'Login successful',
            'user': UserSerializer(user).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class ProfileView(generics.RetrieveUpdateAPIView):
    """User profile endpoint"""
    
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class PlanView(generics.RetrieveAPIView):
    """User plan information endpoint"""
    
    serializer_class = UserPlanSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        user = self.request.user
        user.reset_monthly_counters_if_needed()
        return user


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upgrade_plan(request):
    """Upgrade user plan to Premium"""
    user = request.user
    
    if user.plan == 'PREMIUM':
        return Response({
            'message': 'User is already on Premium plan'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # In a real app, you would integrate with payment processor here
    old_plan = user.plan
    user.plan = 'PREMIUM'
    user.save()
    
    # Create plan history record
    from .models import UserPlanHistory
    UserPlanHistory.objects.create(
        user=user,
        old_plan=old_plan,
        new_plan='PREMIUM',
        reason='Manual upgrade'
    )
    
    return Response({
        'message': 'Plan upgraded successfully',
        'plan': UserPlanSerializer(user).data
    }, status=status.HTTP_200_OK)
