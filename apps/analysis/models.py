from django.db import models
from apps.reviews.models import Review
from apps.clinics.models import Clinic


class SentimentAnalysis(models.Model):
    """
    감성 분석 결과 모델
    """
    review = models.OneToOneField(Review, on_delete=models.CASCADE, verbose_name='리뷰')
    
    # 6가지 측면별 점수 (-1 ~ +1)
    price_score = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='가격 점수')
    skill_score = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='실력 점수')
    kindness_score = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='친절도 점수')
    waiting_time_score = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='대기시간 점수')
    facility_score = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='시설 점수')
    overtreatment_score = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='과잉진료 점수')
    
    # 분석 메타데이터
    model_version = models.CharField(max_length=50, verbose_name='모델 버전')
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='신뢰도')
    analyzed_at = models.DateTimeField(auto_now_add=True, verbose_name='분석일')
    
    class Meta:
        db_table = 'analysis_sentiment'
        verbose_name = '감성 분석'
        verbose_name_plural = '감성 분석들'
        indexes = [
            models.Index(fields=['analyzed_at']),
            models.Index(fields=['model_version']),
        ]
    
    def __str__(self):
        return f"{self.review.clinic.name} - 감성분석 ({self.analyzed_at.date()})"


class PriceData(models.Model):
    """
    가격 데이터 모델
    """
    TREATMENT_CHOICES = [
        ('scaling', '스케일링'),
        ('implant', '임플란트'),
        ('root_canal', '신경치료'),
        ('orthodontics', '교정'),
        ('whitening', '미백'),
        ('extraction', '발치'),
        ('filling', '충치치료'),
        ('crown', '크라운'),
        ('bridge', '브릿지'),
        ('denture', '틀니'),
        ('other', '기타'),
    ]
    
    EXTRACTION_METHOD_CHOICES = [
        ('regex', '정규표현식'),
        ('ner', 'NER 모델'),
        ('manual', '수동 입력'),
    ]
    
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='prices', verbose_name='치과')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=True, blank=True, verbose_name='리뷰')
    
    treatment_type = models.CharField(max_length=100, choices=TREATMENT_CHOICES, verbose_name='치료 종류')
    price = models.IntegerField(verbose_name='가격')
    currency = models.CharField(max_length=3, default='KRW', verbose_name='통화')
    
    # 추출 메타데이터
    extraction_confidence = models.DecimalField(max_digits=3, decimal_places=2, verbose_name='추출 신뢰도')
    extraction_method = models.CharField(max_length=50, choices=EXTRACTION_METHOD_CHOICES, verbose_name='추출 방법')
    
    # 검증 상태
    is_verified = models.BooleanField(default=False, verbose_name='검증됨')
    is_outlier = models.BooleanField(default=False, verbose_name='이상치')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')
    
    class Meta:
        db_table = 'analysis_price'
        verbose_name = '가격 데이터'
        verbose_name_plural = '가격 데이터들'
        indexes = [
            models.Index(fields=['treatment_type']),
            models.Index(fields=['clinic', 'treatment_type']),
            models.Index(fields=['is_verified', 'is_outlier']),
        ]
    
    def __str__(self):
        return f"{self.clinic.name} - {self.get_treatment_type_display()}: {self.price:,}원"


class RegionalPriceStats(models.Model):
    """
    지역별 가격 통계 모델
    """
    district = models.CharField(max_length=100, verbose_name='지역구')
    treatment_type = models.CharField(max_length=100, verbose_name='치료 종류')
    
    # 통계 데이터
    min_price = models.IntegerField(verbose_name='최소 가격')
    max_price = models.IntegerField(verbose_name='최대 가격')
    avg_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='평균 가격')
    median_price = models.IntegerField(verbose_name='중간값 가격')
    
    # 메타데이터
    sample_count = models.IntegerField(verbose_name='샘플 수')
    last_updated = models.DateTimeField(auto_now=True, verbose_name='마지막 업데이트')
    
    class Meta:
        db_table = 'analysis_regional_price_stats'
        verbose_name = '지역별 가격 통계'
        verbose_name_plural = '지역별 가격 통계들'
        unique_together = ['district', 'treatment_type']
        indexes = [
            models.Index(fields=['district', 'treatment_type']),
        ]
    
    def __str__(self):
        return f"{self.district} - {self.treatment_type}: 평균 {self.avg_price:,.0f}원"