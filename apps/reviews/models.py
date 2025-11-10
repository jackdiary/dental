from django.db import models
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.clinics.models import Clinic
import hashlib


class Review(models.Model):
    """
    리뷰 데이터 모델
    """
    SOURCE_CHOICES = [
        ('naver', '네이버 플레이스'),
        ('google', '구글 맵'),
        ('manual', '수동 입력'),
    ]
    
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='reviews', verbose_name='치과')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, verbose_name='출처')
    
    # 리뷰 텍스트
    original_text = models.TextField(verbose_name='원본 텍스트')
    processed_text = models.TextField(blank=True, verbose_name='전처리된 텍스트')
    
    # 원본 메타데이터
    original_rating = models.IntegerField(null=True, blank=True, verbose_name='원본 평점')
    review_date = models.DateTimeField(null=True, blank=True, verbose_name='리뷰 작성일')
    reviewer_hash = models.CharField(max_length=64, verbose_name='리뷰어 해시')  # 익명화된 리뷰어 식별자
    
    # 외부 플랫폼 ID
    external_id = models.CharField(max_length=100, blank=True, verbose_name='외부 플랫폼 ID')
    
    # 처리 상태
    is_processed = models.BooleanField(default=False, verbose_name='전처리 완료')
    is_duplicate = models.BooleanField(default=False, verbose_name='중복 리뷰')
    is_flagged = models.BooleanField(default=False, verbose_name='플래그됨')
    
    # PostgreSQL 전문 검색을 위한 벡터 필드
    search_vector = SearchVectorField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        db_table = 'reviews_review'
        verbose_name = '리뷰'
        verbose_name_plural = '리뷰들'
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['clinic', 'is_processed']),
            models.Index(fields=['source', 'created_at']),
            models.Index(fields=['reviewer_hash']),
        ]
        unique_together = ['clinic', 'external_id', 'source']  # 중복 방지
    
    def __str__(self):
        return f"{self.clinic.name} - {self.source} ({self.created_at.date()})"
    
    def update_search_vector(self):
        """검색 벡터 업데이트"""
        self.search_vector = SearchVector('original_text', weight='A') + \
                           SearchVector('processed_text', weight='B')
        self.save(update_fields=['search_vector'])

    def generate_reviewer_hash(self, reviewer_name):
        """리뷰어 해시 생성"""
        if reviewer_name:
            hash_input = f"{reviewer_name}_{self.clinic.id}_{self.source}"
            self.reviewer_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()

    def save(self, *args, **kwargs):
        # 리뷰어 해시가 없으면 생성
        if not self.reviewer_hash and hasattr(self, '_reviewer_name'):
            self.generate_reviewer_hash(self._reviewer_name)
        
        super().save(*args, **kwargs)


@receiver(post_save, sender=Review)
def update_review_search_vector(sender, instance, created, **kwargs):
    """리뷰 저장 시 검색 벡터 자동 업데이트"""
    if created or not instance.search_vector:
        instance.update_search_vector()


@receiver([post_save, post_delete], sender=Review)
def update_clinic_stats(sender, instance, **kwargs):
    """리뷰 변경 시 치과 통계 업데이트"""
    instance.clinic.update_review_stats()