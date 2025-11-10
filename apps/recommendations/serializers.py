"""
추천 시스템 시리얼라이저
"""
from rest_framework import serializers
from .models import RecommendationLog, ClinicScore, RecommendationFeedback


class UserLocationSerializer(serializers.Serializer):
    """
    사용자 위치 시리얼라이저
    """
    latitude = serializers.FloatField(min_value=-90, max_value=90)
    longitude = serializers.FloatField(min_value=-180, max_value=180)


class RecommendationRequestSerializer(serializers.Serializer):
    """
    추천 요청 시리얼라이저
    """
    district = serializers.CharField(max_length=100, help_text="지역구 (예: 강남구)")
    treatment_type = serializers.CharField(
        max_length=100, 
        required=False, 
        allow_blank=True,
        help_text="치료 종류 (선택적)"
    )
    user_location = UserLocationSerializer(required=False, help_text="사용자 위치 (선택적)")
    limit = serializers.IntegerField(
        min_value=1, 
        max_value=50, 
        default=10,
        help_text="반환할 추천 수 (기본값: 10)"
    )
    
    def validate_district(self, value):
        """
        지역구 유효성 검증
        """
        if not value or len(value.strip()) < 2:
            raise serializers.ValidationError("유효한 지역구를 입력해주세요")
        return value.strip()
    
    def validate_treatment_type(self, value):
        """
        치료 종류 유효성 검증
        """
        if value:
            # 일반적인 치료 종류 목록
            valid_treatments = [
                '스케일링', '임플란트', '신경치료', '교정', '충치치료',
                '사랑니', '틀니', '크라운', '브릿지', '라미네이트',
                '치아미백', '잇몸치료', '발치'
            ]
            
            # 부분 매칭 허용
            value_lower = value.lower()
            for treatment in valid_treatments:
                if treatment in value or value in treatment:
                    return value
            
            # 유효하지 않은 치료 종류도 허용 (새로운 치료법 고려)
            return value
        
        return value


class ClinicRecommendationSerializer(serializers.Serializer):
    """
    치과 추천 결과 시리얼라이저
    """
    clinic_id = serializers.IntegerField()
    clinic_name = serializers.CharField()
    clinic_address = serializers.CharField()
    clinic_phone = serializers.CharField()
    district = serializers.CharField()
    
    # 점수 정보
    comprehensive_score = serializers.FloatField()
    price_competitiveness = serializers.FloatField()
    medical_skill = serializers.FloatField()
    overtreatment_risk = serializers.FloatField()
    patient_satisfaction = serializers.FloatField()
    
    # 메타데이터
    review_count = serializers.IntegerField()
    distance = serializers.FloatField(allow_null=True)
    explanation = serializers.CharField()
    
    # 시설 정보
    has_parking = serializers.BooleanField()
    night_service = serializers.BooleanField()
    weekend_service = serializers.BooleanField()


class RecommendationMetadataSerializer(serializers.Serializer):
    """
    추천 메타데이터 시리얼라이저
    """
    district = serializers.CharField()
    treatment_type = serializers.CharField(allow_null=True)
    total_count = serializers.IntegerField()
    response_time_ms = serializers.IntegerField()
    algorithm_version = serializers.CharField()


class RecommendationResponseSerializer(serializers.Serializer):
    """
    추천 응답 시리얼라이저
    """
    success = serializers.BooleanField()
    recommendations = ClinicRecommendationSerializer(many=True)
    metadata = RecommendationMetadataSerializer()


class ClinicScoreSerializer(serializers.ModelSerializer):
    """
    치과 점수 시리얼라이저
    """
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    clinic_district = serializers.CharField(source='clinic.district', read_only=True)
    
    class Meta:
        model = ClinicScore
        fields = [
            'id', 'clinic_name', 'clinic_district',
            'price_competitiveness', 'medical_skill', 
            'overtreatment_risk', 'patient_satisfaction',
            'comprehensive_score', 'calculation_version',
            'last_calculated', 'total_reviews_analyzed',
            'price_data_points'
        ]
        read_only_fields = ['id', 'last_calculated']


class RecommendationLogSerializer(serializers.ModelSerializer):
    """
    추천 로그 시리얼라이저
    """
    user_email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = RecommendationLog
        fields = [
            'id', 'user_email', 'district', 'treatment_type',
            'recommended_clinics', 'algorithm_version',
            'request_ip', 'response_time_ms', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class RecommendationFeedbackSerializer(serializers.ModelSerializer):
    """
    추천 피드백 시리얼라이저
    """
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    
    class Meta:
        model = RecommendationFeedback
        fields = [
            'id', 'recommendation_log', 'clinic', 'clinic_name',
            'feedback_type', 'comment', 'did_visit', 'visit_rating',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def validate_visit_rating(self, value):
        """
        방문 평점 유효성 검증
        """
        if value is not None and (value < 1 or value > 5):
            raise serializers.ValidationError("평점은 1-5 사이의 값이어야 합니다")
        return value


class PriceComparisonSerializer(serializers.Serializer):
    """
    가격 비교 시리얼라이저
    """
    district = serializers.CharField()
    treatment_type = serializers.CharField()
    
    statistics = serializers.DictField(child=serializers.FloatField(allow_null=True))
    price_levels = serializers.DictField(child=serializers.CharField())


class CrawlingRequestSerializer(serializers.Serializer):
    """
    크롤링 요청 시리얼라이저
    """
    clinic_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="크롤링할 치과 ID 목록 (비어있으면 전체)"
    )
    source = serializers.ChoiceField(
        choices=['naver', 'google', 'all'],
        default='all',
        help_text="크롤링 소스"
    )


class CrawlingStatusSerializer(serializers.Serializer):
    """
    크롤링 상태 시리얼라이저
    """
    task_id = serializers.CharField()
    status = serializers.CharField()
    result = serializers.JSONField(allow_null=True)
    info = serializers.JSONField(allow_null=True)


class SystemStatusSerializer(serializers.Serializer):
    """
    시스템 상태 시리얼라이저
    """
    redis_status = serializers.CharField()
    celery_status = serializers.CharField()
    database_status = serializers.CharField()
    
    total_clinics = serializers.IntegerField()
    total_reviews = serializers.IntegerField()
    processed_reviews = serializers.IntegerField()
    
    last_crawling = serializers.DateTimeField(allow_null=True)
    data_freshness_hours = serializers.FloatField(allow_null=True)
    
    ml_model_status = serializers.DictField()
    cache_hit_rate = serializers.FloatField(allow_null=True)


class PerformanceMetricsSerializer(serializers.Serializer):
    """
    성능 지표 시리얼라이저
    """
    avg_response_time_ms = serializers.FloatField()
    max_response_time_ms = serializers.FloatField()
    min_response_time_ms = serializers.FloatField()
    
    total_requests = serializers.IntegerField()
    successful_requests = serializers.IntegerField()
    error_rate = serializers.FloatField()
    
    cache_hit_rate = serializers.FloatField()
    
    period_start = serializers.DateTimeField()
    period_end = serializers.DateTimeField()


class MLModelMetricsSerializer(serializers.Serializer):
    """
    ML 모델 성능 지표 시리얼라이저
    """
    model_name = serializers.CharField()
    model_version = serializers.CharField()
    
    accuracy = serializers.FloatField(allow_null=True)
    precision = serializers.FloatField(allow_null=True)
    recall = serializers.FloatField(allow_null=True)
    f1_score = serializers.FloatField(allow_null=True)
    
    total_predictions = serializers.IntegerField()
    avg_confidence = serializers.FloatField(allow_null=True)
    
    last_evaluation = serializers.DateTimeField(allow_null=True)
    training_data_size = serializers.IntegerField(allow_null=True)