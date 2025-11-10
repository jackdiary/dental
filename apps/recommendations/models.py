from django.db import models
from django.contrib.auth import get_user_model
from apps.clinics.models import Clinic

User = get_user_model()


class RecommendationLog(models.Model):
    """
    추천 로그 모델
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='사용자')
    district = models.CharField(max_length=100, verbose_name='지역구')
    treatment_type = models.CharField(max_length=100, null=True, blank=True, verbose_name='치료 종류')
    
    # 추천 결과
    recommended_clinics = models.JSONField(verbose_name='추천된 치과 목록')  # 추천된 치과 ID 목록과 점수
    algorithm_version = models.CharField(max_length=50, verbose_name='알고리즘 버전')
    
    # 요청 메타데이터
    request_ip = models.GenericIPAddressField(null=True, blank=True, verbose_name='요청 IP')
    user_agent = models.TextField(blank=True, verbose_name='사용자 에이전트')
    
    # 성능 메트릭
    response_time_ms = models.IntegerField(null=True, blank=True, verbose_name='응답 시간(ms)')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    
    class Meta:
        db_table = 'recommendations_log'
        verbose_name = '추천 로그'
        verbose_name_plural = '추천 로그들'
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['district', 'created_at']),
            models.Index(fields=['algorithm_version']),
        ]
    
    def __str__(self):
        user_info = self.user.email if self.user else '익명'
        return f"{user_info} - {self.district} ({self.created_at.date()})"


class ClinicScore(models.Model):
    """
    치과 종합 점수 모델 (캐싱용)
    """
    clinic = models.OneToOneField(Clinic, on_delete=models.CASCADE, verbose_name='치과')
    
    # 측면별 점수 (0-100)
    price_competitiveness = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='가격 경쟁력')
    medical_skill = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='의료진 실력')
    overtreatment_risk = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='과잉진료 위험도')
    patient_satisfaction = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='환자 만족도')
    
    # 종합 점수
    comprehensive_score = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='종합 점수')
    
    # 메타데이터
    calculation_version = models.CharField(max_length=50, verbose_name='계산 버전')
    last_calculated = models.DateTimeField(auto_now=True, verbose_name='마지막 계산일')
    
    # 통계 정보
    total_reviews_analyzed = models.IntegerField(default=0, verbose_name='분석된 리뷰 수')
    price_data_points = models.IntegerField(default=0, verbose_name='가격 데이터 포인트 수')
    
    class Meta:
        db_table = 'recommendations_clinic_score'
        verbose_name = '치과 점수'
        verbose_name_plural = '치과 점수들'
        indexes = [
            models.Index(fields=['comprehensive_score']),
        ]
    
    def __str__(self):
        return f"{self.clinic.name} - 종합점수: {self.comprehensive_score}"


class RecommendationFeedback(models.Model):
    """
    추천 피드백 모델
    """
    FEEDBACK_CHOICES = [
        ('helpful', '도움됨'),
        ('not_helpful', '도움안됨'),
        ('inaccurate', '부정확함'),
        ('missing_info', '정보부족'),
    ]
    
    recommendation_log = models.ForeignKey(RecommendationLog, on_delete=models.CASCADE, verbose_name='추천 로그')
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, verbose_name='치과')
    
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_CHOICES, verbose_name='피드백 유형')
    comment = models.TextField(blank=True, verbose_name='코멘트')
    
    # 실제 방문 여부
    did_visit = models.BooleanField(null=True, blank=True, verbose_name='실제 방문')
    visit_rating = models.IntegerField(null=True, blank=True, verbose_name='방문 후 평점')
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일')
    
    class Meta:
        db_table = 'recommendations_feedback'
        verbose_name = '추천 피드백'
        verbose_name_plural = '추천 피드백들'
        unique_together = ['recommendation_log', 'clinic']
    
    def __str__(self):
        return f"{self.clinic.name} - {self.get_feedback_type_display()}"