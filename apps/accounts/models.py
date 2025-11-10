from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for dental recommendation system
    """
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    preferred_district = models.CharField(max_length=100, blank=True)
    
    # User preferences
    is_premium = models.BooleanField(default=False)
    notification_enabled = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = '사용자'
        verbose_name_plural = '사용자들'
    
    def __str__(self):
        return self.email


class UserProfile(models.Model):
    """
    사용자 프로필 확장 모델
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    birth_date = models.DateField(null=True, blank=True, verbose_name='생년월일')
    phone = models.CharField(max_length=20, blank=True, verbose_name='전화번호')
    preferred_district = models.CharField(max_length=100, blank=True, verbose_name='선호 지역')
    
    # 추가 정보
    gender = models.CharField(
        max_length=10, 
        choices=[('M', '남성'), ('F', '여성'), ('O', '기타')],
        blank=True,
        verbose_name='성별'
    )
    
    # 치과 관련 선호도
    preferred_treatments = models.TextField(blank=True, verbose_name='관심 치료')
    budget_range = models.CharField(
        max_length=20,
        choices=[
            ('low', '50만원 이하'),
            ('medium', '50-200만원'),
            ('high', '200만원 이상')
        ],
        blank=True,
        verbose_name='예산 범위'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_user_profile'
        verbose_name = '사용자 프로필'
        verbose_name_plural = '사용자 프로필들'
    
    def __str__(self):
        return f"{self.user.username}의 프로필"