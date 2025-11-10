"""
추천 시스템 테스트
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData
from .models import RecommendationLog, ClinicScore
from .services import RecommendationEngine
from .utils import LocationUtils, PriceAnalyzer, RecommendationValidator

User = get_user_model()


class RecommendationEngineTest(TestCase):
    """
    추천 엔진 테스트
    """
    
    def setUp(self):
        """
        테스트 데이터 설정
        """
        self.engine = RecommendationEngine()
        
        # 테스트 치과 생성
        self.clinic1 = Clinic.objects.create(
            name="우수치과",
            address="서울시 강남구 테헤란로 123",
            district="강남구",
            latitude=Decimal('37.5173'),
            longitude=Decimal('127.0473'),
            phone="02-1234-5678",
            has_parking=True,
            night_service=True,
            weekend_service=False
        )
        
        self.clinic2 = Clinic.objects.create(
            name="평범치과",
            address="서울시 강남구 역삼동 456",
            district="강남구",
            latitude=Decimal('37.5000'),
            longitude=Decimal('127.0300'),
            phone="02-2345-6789",
            has_parking=False,
            night_service=False,
            weekend_service=True
        )
        
        # 테스트 리뷰 생성 (최소 10개 이상)
        for i in range(15):
            review1 = Review.objects.create(
                clinic=self.clinic1,
                source='naver',
                original_text=f"좋은 치과입니다 {i}",
                processed_text=f"좋은 치과입니다 {i}",
                is_processed=True,
                reviewer_hash=f"hash1_{i}"
            )
            
            # 우수한 감성 분석 결과
            SentimentAnalysis.objects.create(
                review=review1,
                price_score=Decimal('0.8'),
                skill_score=Decimal('0.9'),
                kindness_score=Decimal('0.8'),
                waiting_time_score=Decimal('0.7'),
                facility_score=Decimal('0.8'),
                overtreatment_score=Decimal('0.9'),  # 과잉진료 없음 (긍정적)
                model_version='test_v1',
                confidence_score=Decimal('0.9')
            )
            
            review2 = Review.objects.create(
                clinic=self.clinic2,
                source='google',
                original_text=f"보통 치과입니다 {i}",
                processed_text=f"보통 치과입니다 {i}",
                is_processed=True,
                reviewer_hash=f"hash2_{i}"
            )
            
            # 평범한 감성 분석 결과
            SentimentAnalysis.objects.create(
                review=review2,
                price_score=Decimal('0.2'),
                skill_score=Decimal('0.3'),
                kindness_score=Decimal('0.4'),
                waiting_time_score=Decimal('0.2'),
                facility_score=Decimal('0.3'),
                overtreatment_score=Decimal('0.1'),  # 과잉진료 의심 (부정적)
                model_version='test_v1',
                confidence_score=Decimal('0.8')
            )
        
        # 가격 데이터 생성
        PriceData.objects.create(
            clinic=self.clinic1,
            treatment_type="스케일링",
            price=25000,
            extraction_confidence=Decimal('0.9'),
            extraction_method='regex'
        )
        
        PriceData.objects.create(
            clinic=self.clinic2,
            treatment_type="스케일링",
            price=35000,
            extraction_confidence=Decimal('0.8'),
            extraction_method='regex'
        )
    
    def test_get_recommendations_basic(self):
        """
        기본 추천 기능 테스트
        """
        recommendations = self.engine.get_recommendations(
            district="강남구",
            limit=10
        )
        
        # 결과 검증
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # 첫 번째 추천이 우수치과인지 확인 (점수가 더 높아야 함)
        if len(recommendations) >= 2:
            first_rec = recommendations[0]
            second_rec = recommendations[1]
            
            self.assertGreaterEqual(
                first_rec['comprehensive_score'],
                second_rec['comprehensive_score']
            )
    
    def test_filter_by_review_count(self):
        """
        최소 리뷰 수 필터링 테스트
        """
        # 리뷰가 부족한 치과 생성
        clinic_few_reviews = Clinic.objects.create(
            name="리뷰부족치과",
            address="서울시 강남구 삼성동 789",
            district="강남구",
            phone="02-3456-7890"
        )
        
        # 리뷰 5개만 생성 (최소 10개 미만)
        for i in range(5):
            Review.objects.create(
                clinic=clinic_few_reviews,
                source='naver',
                original_text=f"리뷰 {i}",
                processed_text=f"리뷰 {i}",
                is_processed=True,
                reviewer_hash=f"hash_few_{i}"
            )
        
        recommendations = self.engine.get_recommendations(
            district="강남구",
            limit=10
        )
        
        # 리뷰가 부족한 치과는 추천에서 제외되어야 함
        clinic_ids = [rec['clinic_id'] for rec in recommendations]
        self.assertNotIn(clinic_few_reviews.id, clinic_ids)
    
    def test_treatment_type_filtering(self):
        """
        치료 종류별 필터링 테스트
        """
        recommendations = self.engine.get_recommendations(
            district="강남구",
            treatment_type="스케일링",
            limit=10
        )
        
        self.assertIsInstance(recommendations, list)
        # 가격 데이터가 있는 치과들이 우선되어야 함
    
    def test_score_calculation(self):
        """
        점수 계산 테스트
        """
        clinic_score = self.engine._calculate_clinic_score(self.clinic1)
        
        self.assertIsNotNone(clinic_score)
        self.assertIsInstance(clinic_score, ClinicScore)
        
        # 점수 범위 확인
        self.assertGreaterEqual(clinic_score.comprehensive_score, 0)
        self.assertLessEqual(clinic_score.comprehensive_score, 100)
        self.assertGreaterEqual(clinic_score.price_competitiveness, 0)
        self.assertLessEqual(clinic_score.price_competitiveness, 100)
    
    def test_explanation_generation(self):
        """
        추천 이유 생성 테스트
        """
        recommendations = self.engine.get_recommendations(
            district="강남구",
            limit=1
        )
        
        if recommendations:
            rec = recommendations[0]
            self.assertIn('explanation', rec)
            self.assertIsInstance(rec['explanation'], str)
            self.assertGreater(len(rec['explanation']), 0)
    
    def test_recommendation_logging(self):
        """
        추천 로그 테스트
        """
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        recommendations = self.engine.get_recommendations(
            district="강남구",
            limit=5
        )
        
        log = self.engine.log_recommendation(
            user=user,
            district="강남구",
            treatment_type=None,
            recommendations=recommendations,
            response_time_ms=1500,
            request_ip="127.0.0.1"
        )
        
        self.assertIsInstance(log, RecommendationLog)
        self.assertEqual(log.user, user)
        self.assertEqual(log.district, "강남구")
        self.assertEqual(log.response_time_ms, 1500)


class LocationUtilsTest(TestCase):
    """
    위치 유틸리티 테스트
    """
    
    def test_get_district_center(self):
        """
        지역구 중심 좌표 테스트
        """
        # 정확한 매칭
        coords = LocationUtils.get_district_center("강남구")
        self.assertIsNotNone(coords)
        self.assertEqual(len(coords), 2)
        
        # 부분 매칭
        coords = LocationUtils.get_district_center("강남")
        self.assertIsNotNone(coords)
        
        # 존재하지 않는 지역
        coords = LocationUtils.get_district_center("존재하지않는구")
        self.assertIsNone(coords)
    
    def test_calculate_distance_score(self):
        """
        거리 점수 계산 테스트
        """
        # 1km 이내
        score = LocationUtils.calculate_distance_score(0.5)
        self.assertEqual(score, 100.0)
        
        # 5km 초과
        score = LocationUtils.calculate_distance_score(6.0)
        self.assertEqual(score, 50.0)


class PriceAnalyzerTest(TestCase):
    """
    가격 분석기 테스트
    """
    
    def setUp(self):
        """
        테스트 데이터 설정
        """
        self.clinic = Clinic.objects.create(
            name="테스트치과",
            district="강남구",
            address="테스트 주소"
        )
        
        # 가격 데이터 생성
        for price in [20000, 25000, 30000, 35000, 40000]:
            PriceData.objects.create(
                clinic=self.clinic,
                treatment_type="스케일링",
                price=price,
                extraction_confidence=Decimal('0.9'),
                extraction_method='regex'
            )
    
    def test_get_regional_price_stats(self):
        """
        지역별 가격 통계 테스트
        """
        stats = PriceAnalyzer.get_regional_price_stats("강남구", "스케일링")
        
        self.assertIn('average', stats)
        self.assertIn('minimum', stats)
        self.assertIn('maximum', stats)
        self.assertIn('count', stats)
        
        self.assertEqual(stats['minimum'], 20000)
        self.assertEqual(stats['maximum'], 40000)
        self.assertEqual(stats['count'], 5)
    
    def test_classify_price_level(self):
        """
        가격 수준 분류 테스트
        """
        stats = PriceAnalyzer.get_regional_price_stats("강남구", "스케일링")
        
        # 평균 가격 (30000)
        level = PriceAnalyzer.classify_price_level(30000, stats)
        self.assertIn(level, ['low', 'average', 'high'])
        
        # 저렴한 가격
        level = PriceAnalyzer.classify_price_level(20000, stats)
        self.assertEqual(level, 'low')
        
        # 비싼 가격
        level = PriceAnalyzer.classify_price_level(40000, stats)
        self.assertEqual(level, 'high')


class RecommendationValidatorTest(TestCase):
    """
    추천 검증기 테스트
    """
    
    def test_validate_recommendation_data(self):
        """
        추천 데이터 유효성 검증 테스트
        """
        # 유효한 데이터
        valid_rec = {
            'clinic_id': 1,
            'clinic_name': '테스트치과',
            'comprehensive_score': 85.5,
            'price_competitiveness': 80.0,
            'medical_skill': 90.0,
            'overtreatment_risk': 20.0,
            'patient_satisfaction': 85.0
        }
        
        self.assertTrue(RecommendationValidator.validate_recommendation_data(valid_rec))
        
        # 필수 필드 누락
        invalid_rec = {
            'clinic_id': 1,
            'clinic_name': '테스트치과'
            # 점수 필드들 누락
        }
        
        self.assertFalse(RecommendationValidator.validate_recommendation_data(invalid_rec))
        
        # 점수 범위 오류
        invalid_score_rec = {
            'clinic_id': 1,
            'clinic_name': '테스트치과',
            'comprehensive_score': 150.0,  # 100 초과
            'price_competitiveness': 80.0,
            'medical_skill': 90.0,
            'overtreatment_risk': 20.0,
            'patient_satisfaction': 85.0
        }
        
        self.assertFalse(RecommendationValidator.validate_recommendation_data(invalid_score_rec))
    
    def test_filter_valid_recommendations(self):
        """
        유효한 추천 필터링 테스트
        """
        recommendations = [
            {
                'clinic_id': 1,
                'clinic_name': '유효치과',
                'comprehensive_score': 85.5,
                'price_competitiveness': 80.0,
                'medical_skill': 90.0,
                'overtreatment_risk': 20.0,
                'patient_satisfaction': 85.0
            },
            {
                'clinic_id': 2,
                'clinic_name': '무효치과',
                'comprehensive_score': 150.0,  # 유효하지 않은 점수
            }
        ]
        
        valid_recs = RecommendationValidator.filter_valid_recommendations(recommendations)
        
        self.assertEqual(len(valid_recs), 1)
        self.assertEqual(valid_recs[0]['clinic_name'], '유효치과')