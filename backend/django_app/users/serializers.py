from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password_confirm', 'first_name', 'last_name')
        extra_kwargs = {
            'password': {'write_only': True},
            'password_confirm': {'write_only': True},
        }
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(username=email, password=password)
            
            if not user:
                raise serializers.ValidationError('Invalid credentials')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled')
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError('Must include email and password')


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user profile"""
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'username', 'first_name', 'last_name', 
            'plan', 'plan_started_at', 'documents_uploaded_this_month',
            'ai_tokens_used_this_month', 'created_at'
        )
        read_only_fields = (
            'id', 'plan', 'plan_started_at', 'documents_uploaded_this_month',
            'ai_tokens_used_this_month', 'created_at'
        )


class UserPlanSerializer(serializers.ModelSerializer):
    """Serializer for user plan information"""
    
    can_upload_document = serializers.SerializerMethodField()
    monthly_limits = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'plan', 'plan_started_at', 'documents_uploaded_this_month',
            'ai_tokens_used_this_month', 'can_upload_document', 'monthly_limits'
        )
    
    def get_can_upload_document(self, obj):
        return obj.can_upload_document()
    
    def get_monthly_limits(self, obj):
        from django.conf import settings
        return settings.PLAN_LIMITS[obj.plan]
