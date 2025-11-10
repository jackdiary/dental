from django.db import models
from django.contrib.postgres.search import SearchVectorField, SearchVector
from django.contrib.postgres.indexes import GinIndex
from django.db.models.signals import post_save
from django.dispatch import receiver


class Clinic(models.Model):
    """
    치과 정보 모델
    """
    name = models.CharField(max_length=200, verbose_name='치과명')
    address = models.TextField(verbose_name='주소')
    district = models.CharField(max_length=100, verbose_name='지역구')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='위도')
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, verbose_name='경도')
    phone = models.CharField(max_length=20, blank=True, verbose_name='전화번호')
    
    # 시설 정보
    has_parking = models.BooleanField(default=False, verbose_name='주차 가능')
    night_service = models.BooleanField(default=False, verbose_name='야간 진료')
    weekend_service = models.BooleanField(default=False, verbose_name='주말 진료')
    
    # 통계 정보
    total_reviews = models.IntegerField(default=0, verbose_name='총 리뷰 수')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name='평균 평점')
    
    # 검증 상태
    is_verified = models.BooleanField(default=False, verbose_name='검증됨')
    
    # 추가 정보
    website = models.URLField(blank=True, verbose_name='웹사이트')
    business_hours = models.TextField(blank=True, verbose_name='운영시간')
    description = models.TextField(blank=True, verbose_name='설명')
    specialties = models.TextField(blank=True, verbose_name='전문분야')
    facilities = models.TextField(blank=True, verbose_name='시설정보')
    
    # 외부 플랫폼 ID
    naver_place_id = models.CharField(max_length=100, blank=True, verbose_name='네이버 플레이스 ID')
    google_place_id = models.CharField(max_length=100, blank=True, verbose_name='구글 플레이스 ID')
    
    # 검색을 위한 벡터 필드
    search_vector = SearchVectorField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        db_table = 'clinics_clinic'
        verbose_name = '치과'
        verbose_name_plural = '치과들'
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['district']),
            models.Index(fields=['total_reviews']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.district})"
    
    def update_search_vector(self):
        """검색 벡터 업데이트"""
        self.search_vector = SearchVector('name', weight='A') + \
                           SearchVector('address', weight='B') + \
                           SearchVector('district', weight='C')
        self.save(update_fields=['search_vector'])

    def update_review_stats(self):
        """리뷰 통계 업데이트"""
        from apps.reviews.models import Review
        reviews = Review.objects.filter(clinic=self, is_processed=True, is_duplicate=False)
        
        self.total_reviews = reviews.count()
        if self.total_reviews > 0:
            # 평균 평점 계산 (원본 평점이 있는 경우만)
            rated_reviews = reviews.filter(original_rating__isnull=False)
            if rated_reviews.exists():
                self.average_rating = rated_reviews.aggregate(
                    avg_rating=models.Avg('original_rating')
                )['avg_rating']
        
        self.save(update_fields=['total_reviews', 'average_rating'])


@receiver(post_save, sender=Clinic)
def update_clinic_search_vector(sender, instance, created, **kwargs):
    """치과 저장 시 검색 벡터 자동 업데이트"""
    if created or not instance.search_vector:
        instance.update_search_vector()