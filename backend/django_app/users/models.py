from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from datetime import datetime, timedelta


class User(AbstractUser):
    """Custom User model with plan information"""
    
    PLAN_CHOICES = [
        ('FREE', 'Free'),
        ('PREMIUM', 'Premium'),
    ]
    
    email = models.EmailField(unique=True)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='FREE')
    plan_started_at = models.DateTimeField(default=timezone.now)
    documents_uploaded_this_month = models.IntegerField(default=0)
    ai_tokens_used_this_month = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        
    def __str__(self):
        return self.email
    
    def reset_monthly_counters_if_needed(self):
        """Reset monthly counters if a new month has started"""
        now = timezone.now()
        if self.plan_started_at.month != now.month or self.plan_started_at.year != now.year:
            self.documents_uploaded_this_month = 0
            self.ai_tokens_used_this_month = 0
            self.plan_started_at = now
            self.save()
    
    def can_upload_document(self):
        """Check if user can upload a new document based on plan limits"""
        from django.conf import settings
        
        self.reset_monthly_counters_if_needed()
        
        limit = settings.PLAN_LIMITS[self.plan]['documents_per_month']
        if limit == -1:  # Unlimited
            return True
        return self.documents_uploaded_this_month < limit
    
    def can_use_ai_tokens(self, tokens_needed):
        """Check if user can use AI tokens based on plan limits"""
        from django.conf import settings
        
        self.reset_monthly_counters_if_needed()
        
        limit = settings.PLAN_LIMITS[self.plan]['ai_tokens_per_month']
        if limit == -1:  # Unlimited
            return True
        return (self.ai_tokens_used_this_month + tokens_needed) <= limit
    
    def use_ai_tokens(self, tokens_used):
        """Increment AI tokens usage"""
        self.ai_tokens_used_this_month += tokens_used
        self.save()
    
    def increment_document_count(self):
        """Increment document upload count"""
        self.documents_uploaded_this_month += 1
        self.save()


class UserPlanHistory(models.Model):
    """Track user plan changes"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='plan_history')
    old_plan = models.CharField(max_length=10, choices=User.PLAN_CHOICES)
    new_plan = models.CharField(max_length=10, choices=User.PLAN_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)
    reason = models.CharField(max_length=255, blank=True)
    
    class Meta:
        db_table = 'user_plan_history'
        ordering = ['-changed_at']
    
    def __str__(self):
        return f"{self.user.email}: {self.old_plan} -> {self.new_plan}"
