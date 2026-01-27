from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager


class CustomUserManager(BaseUserManager):
    """Custom user manager for email-based authentication"""
    
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(email, full_name, password, **extra_fields)


class CustomUser(AbstractUser):
    """
    Custom User Model for the inventory system.
    Uses email as the unique identifier instead of username.
    
    Roles:
    - ADMIN: Full access to all features
    - STAFF: Can create sales, view products
    - VIEWER: Read-only access
    """
    
    ROLE_CHOICES = [
        ('ADMIN', 'Administrator'),
        ('STAFF', 'Staff'),
        ('VIEWER', 'Viewer'),
    ]
    
    username = None  # Remove username field
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='VIEWER')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.full_name} ({self.email})"
    
    def has_admin_access(self):
        """Check if user has admin access"""
        return self.role == 'ADMIN' or self.is_superuser
    
    def has_staff_access(self):
        """Check if user has staff access"""
        return self.role in ['ADMIN', 'STAFF'] or self.is_staff
    
    def has_viewer_access(self):
        """Check if user has viewer access"""
        return True  # All authenticated users can view