"""
치과 추천 서비스 모듈
"""
import logging
from typing import List, Dict, Optional, Tuple
from decimal import Decimal
from django.db.models import Q, Avg, Count, F
from django.core.cache import cache
from django.utils import timezone
from geopy.distance import geodesic

from apps.clinics.models import Clinic
from apps.clinics.location_services import location_service, LocationUtils
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData
from .models import RecommendationLog, ClinicScore

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """
    치과 추천 엔진
    """
    
    # 알고리즘 버전
    ALGORITHM_VERSION = "v1.0"
    
    # 가중치 설정 (요구사항: 가격합리성 30%, 의료진실력 25%, 과잉진료위험도 25%, 환자만족도 20%)
    WEIGHTS = {
        'price_competitiveness': 0.30,
        'medical_skill': 0.25,
        'overtreatment_risk': 0.25,
        'patient_satisfaction': 0.20
    }
    
    # 최소 리뷰 수 (요구사항: 10개 이상)
    MIN_REVIEWS = 10
    
    # 검색 반경 (요구사항: 5km)
    SEARCH_RADIUS_KM = 5
    
    def __init__(self):
        self.cache_timeout = 3600  # 1시간 캐시
    
    def get_recommendations(
        self, 
        district: str, 
        treatment_type: Optional[str] = None,
        user_location: Optional[Tuple[float, float]] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        치과 추천 목록 반환
        
        Args:
            district: 지역구 (예: "강남구")
            treatment_type: 치료 종류 (선택적)
            user_location: 사용자 위치 (위도, 경도)
            limit: 반환할 추천 수
            
        Returns:
            추천 치과 목록
        """
        logger.info(f"추천 요청: 지역={district}, 치료={treatment_type}, 제한={limit}")
        
        # 캐시 키 생성
        cache_key = self._generate_cache_key(district, treatment_type, limit)
        cached_result = cache.get(cache_key)
        
        if cached_result:
            logger.info("캐시된 추천 결과 반환")
            return cached_result
        
        # 1. 지역 기반 치과 필터링
        clinics = self._filter_clinics_by_location(district, user_location)
        
        # 2. 최소 리뷰 수 필터링
        clinics = self._filter_by_review_count(clinics)
        
        # 3. 치료 종류 필터링 (선택적)
        if treatment_type:
            clinics = self._filter_by_treatment_type(clinics, treatment_type)
        
        # 4. 점수 계산 및 정렬
        recommendations = self._calculate_and_rank_clinics(clinics, treatment_type)
        
        # 5. 상위 N개 선택
        recommendations = recommendations[:limit]
        
        # 6. 추천 이유 생성
        for rec in recommendations:
            rec['explanation'] = self._generate_explanation(rec)
        
        # 캐시 저장
        cache.set(cache_key, recommendations, self.cache_timeout)
        
        logger.info(f"추천 완료: {len(recommendations)}개 치과")
        return recommendations
    
    def _filter_clinics_by_location(
        self, 
        district: str, 
        user_location: Optional[Tuple[float, float]] = None
    ) -> List[Clinic]:
        """
        지역 기반 치과 필터링
        """
        # 기본적으로 지역구로 필터링
        clinics = Clinic.objects.filter(district__icontains=district)
        
        # 사용자 위치가 제공된 경우 반경 내 치과 추가 필터링
        if user_location:
            user_lat, user_lng = user_location
            filtered_clinics = []
            
            for clinic in clinics:
                if clinic.latitude and clinic.longitude:
                    clinic_location = (float(clinic.latitude), float(clinic.longitude))
                    distance = geodesic(user_location, clinic_location).kilometers
                    
                    if distance <= self.SEARCH_RADIUS_KM:
                        clinic.distance = distance  # 거리 정보 추가
                        filtered_clinics.append(clinic)
            
            return filtered_clinics
        
        return list(clinics)
    
    def _filter_by_review_count(self, clinics: List[Clinic]) -> List[Clinic]:
        """
        최소 리뷰 수 필터링
        """
        clinic_ids = [clinic.id for clinic in clinics]
        
        # 리뷰 수 계산
        review_counts = Review.objects.filter(
            clinic_id__in=clinic_ids,
            is_processed=True
        ).values('clinic_id').annotate(
            review_count=Count('id')
        ).filter(
            review_count__gte=self.MIN_REVIEWS
        )
        
        valid_clinic_ids = {item['clinic_id'] for item in review_counts}
        
        # 리뷰 수 정보 추가
        for clinic in clinics:
            clinic.review_count = next(
                (item['review_count'] for item in review_counts 
                 if item['clinic_id'] == clinic.id), 0
            )
        
        return [clinic for clinic in clinics if clinic.id in valid_clinic_ids]
    
    def _filter_by_treatment_type(self, clinics: List[Clinic], treatment_type: str) -> List[Clinic]:
        """
        치료 종류별 필터링 (가격 데이터가 있는 치과 우선)
        """
        clinic_ids = [clinic.id for clinic in clinics]
        
        # 해당 치료의 가격 데이터가 있는 치과 조회
        clinics_with_price_data = PriceData.objects.filter(
            clinic_id__in=clinic_ids,
            treatment_type__icontains=treatment_type
        ).values_list('clinic_id', flat=True).distinct()
        
        # 가격 데이터가 있는 치과를 우선 순위로 정렬
        clinics_with_data = [c for c in clinics if c.id in clinics_with_price_data]
        clinics_without_data = [c for c in clinics if c.id not in clinics_with_price_data]
        
        return clinics_with_data + clinics_without_data
    
    def _calculate_and_rank_clinics(
        self, 
        clinics: List[Clinic], 
        treatment_type: Optional[str] = None
    ) -> List[Dict]:
        """
        치과 점수 계산 및 순위 결정
        """
        recommendations = []
        
        for clinic in clinics:
            # 기존 점수 조회 또는 새로 계산
            clinic_score = self._get_or_calculate_clinic_score(clinic, treatment_type)
            
            if clinic_score:
                recommendation = {
                    'clinic_id': clinic.id,
                    'clinic_name': clinic.name,
                    'clinic_address': clinic.address,
                    'clinic_phone': clinic.phone,
                    'district': clinic.district,
                    'comprehensive_score': float(clinic_score.comprehensive_score),
                    'price_competitiveness': float(clinic_score.price_competitiveness),
                    'medical_skill': float(clinic_score.medical_skill),
                    'overtreatment_risk': float(clinic_score.overtreatment_risk),
                    'patient_satisfaction': float(clinic_score.patient_satisfaction),
                    'review_count': getattr(clinic, 'review_count', 0),
                    'distance': getattr(clinic, 'distance', None),
                    'has_parking': clinic.has_parking,
                    'night_service': clinic.night_service,
                    'weekend_service': clinic.weekend_service,
                }
                recommendations.append(recommendation)
        
        # 종합 점수로 정렬
        recommendations.sort(key=lambda x: x['comprehensive_score'], reverse=True)
        
        return recommendations
    
    def _get_or_calculate_clinic_score(
        self, 
        clinic: Clinic, 
        treatment_type: Optional[str] = None
    ) -> Optional[ClinicScore]:
        """
        치과 점수 조회 또는 계산
        """
        try:
            # 기존 점수 조회 (24시간 이내)
            clinic_score = ClinicScore.objects.filter(
                clinic=clinic,
                last_calculated__gte=timezone.now() - timezone.timedelta(hours=24)
            ).first()
            
            if clinic_score:
                return clinic_score
            
            # 새로 계산
            return self._calculate_clinic_score(clinic, treatment_type)
            
        except Exception as e:
            logger.error(f"치과 점수 계산 오류 (clinic_id={clinic.id}): {e}")
            return None
    
    def _calculate_clinic_score(
        self, 
        clinic: Clinic, 
        treatment_type: Optional[str] = None
    ) -> Optional[ClinicScore]:
        """
        치과 종합 점수 계산
        """
        try:
            # 감성 분석 데이터 조회
            sentiment_data = SentimentAnalysis.objects.filter(
                review__clinic=clinic,
                review__is_processed=True
            ).aggregate(
                avg_price=Avg('price_score'),
                avg_skill=Avg('skill_score'),
                avg_kindness=Avg('kindness_score'),
                avg_waiting=Avg('waiting_time_score'),
                avg_facility=Avg('facility_score'),
                avg_overtreatment=Avg('overtreatment_score'),
                count=Count('id')
            )
            
            if not sentiment_data['count'] or sentiment_data['count'] < self.MIN_REVIEWS:
                return None
            
            # 가격 데이터 조회
            price_data_count = PriceData.objects.filter(clinic=clinic).count()
            
            # 각 측면별 점수 계산 (0-100 스케일로 정규화)
            price_competitiveness = self._normalize_price_score(
                sentiment_data['avg_price'], clinic, treatment_type
            )
            medical_skill = self._normalize_sentiment_score(sentiment_data['avg_skill'])
            patient_satisfaction = self._calculate_patient_satisfaction(
                sentiment_data['avg_kindness'],
                sentiment_data['avg_waiting'],
                sentiment_data['avg_facility']
            )
            overtreatment_risk = self._normalize_overtreatment_score(
                sentiment_data['avg_overtreatment']
            )
            
            # 종합 점수 계산
            comprehensive_score = (
                float(price_competitiveness) * self.WEIGHTS['price_competitiveness'] +
                float(medical_skill) * self.WEIGHTS['medical_skill'] +
                (100 - float(overtreatment_risk)) * self.WEIGHTS['overtreatment_risk'] +  # 위험도는 역수
                float(patient_satisfaction) * self.WEIGHTS['patient_satisfaction']
            )
            
            # ClinicScore 객체 생성 또는 업데이트
            clinic_score, created = ClinicScore.objects.update_or_create(
                clinic=clinic,
                defaults={
                    'price_competitiveness': Decimal(str(round(price_competitiveness, 2))),
                    'medical_skill': Decimal(str(round(medical_skill, 2))),
                    'overtreatment_risk': Decimal(str(round(overtreatment_risk, 2))),
                    'patient_satisfaction': Decimal(str(round(patient_satisfaction, 2))),
                    'comprehensive_score': Decimal(str(round(comprehensive_score, 2))),
                    'calculation_version': self.ALGORITHM_VERSION,
                    'total_reviews_analyzed': sentiment_data['count'],
                    'price_data_points': price_data_count,
                }
            )
            
            return clinic_score
            
        except Exception as e:
            logger.error(f"치과 점수 계산 실패 (clinic_id={clinic.id}): {e}")
            return None
    
    def _normalize_sentiment_score(self, score: Optional[float]) -> float:
        """
        감성 점수를 0-100 스케일로 정규화
        """
        if score is None:
            return 50.0  # 중립값
        
        # -1 ~ +1 범위를 0 ~ 100으로 변환
        return max(0, min(100, (score + 1) * 50))
    
    def _normalize_price_score(
        self, 
        price_sentiment: Optional[float], 
        clinic: Clinic, 
        treatment_type: Optional[str] = None
    ) -> float:
        """
        가격 경쟁력 점수 계산
        """
        base_score = self._normalize_sentiment_score(price_sentiment)
        
        # 치료 종류별 가격 비교가 가능한 경우 추가 보정
        if treatment_type:
            try:
                # 해당 치과의 평균 가격
                clinic_avg_price = PriceData.objects.filter(
                    clinic=clinic,
                    treatment_type__icontains=treatment_type
                ).aggregate(avg_price=Avg('price'))['avg_price']
                
                # 지역 평균 가격
                regional_avg_price = PriceData.objects.filter(
                    clinic__district=clinic.district,
                    treatment_type__icontains=treatment_type
                ).aggregate(avg_price=Avg('price'))['avg_price']
                
                if clinic_avg_price and regional_avg_price:
                    price_ratio = clinic_avg_price / regional_avg_price
                    
                    # 지역 평균보다 저렴하면 보너스, 비싸면 페널티
                    if price_ratio < 0.9:  # 10% 이상 저렴
                        base_score = min(100, base_score + 20)
                    elif price_ratio > 1.3:  # 30% 이상 비쌈 (과도한 가격책정)
                        base_score = max(0, base_score - 30)
                    
            except Exception as e:
                logger.warning(f"가격 비교 계산 실패: {e}")
        
        return base_score
    
    def _normalize_overtreatment_score(self, overtreatment_sentiment: Optional[float]) -> float:
        """
        과잉진료 위험도 점수 계산 (0-100, 높을수록 위험)
        """
        if overtreatment_sentiment is None:
            return 50.0  # 중립값
        
        # 부정적 감성일수록 과잉진료 위험도가 높음
        # -1(매우 부정적) -> 100(매우 위험), +1(매우 긍정적) -> 0(안전)
        return max(0, min(100, (1 - overtreatment_sentiment) * 50))
    
    def _calculate_patient_satisfaction(
        self, 
        kindness: Optional[float], 
        waiting_time: Optional[float], 
        facility: Optional[float]
    ) -> float:
        """
        환자 만족도 계산 (친절도, 대기시간, 시설의 평균)
        """
        scores = []
        
        if kindness is not None:
            scores.append(self._normalize_sentiment_score(kindness))
        if waiting_time is not None:
            scores.append(self._normalize_sentiment_score(waiting_time))
        if facility is not None:
            scores.append(self._normalize_sentiment_score(facility))
        
        if not scores:
            return 50.0  # 기본값
        
        return sum(scores) / len(scores)
    
    def _generate_explanation(self, recommendation: Dict) -> str:
        """
        추천 이유 생성
        """
        clinic_name = recommendation['clinic_name']
        score = recommendation['comprehensive_score']
        
        explanations = []
        
        # 종합 점수 기반 설명
        if score >= 80:
            explanations.append("종합적으로 매우 우수한 치과입니다")
        elif score >= 70:
            explanations.append("전반적으로 좋은 평가를 받는 치과입니다")
        elif score >= 60:
            explanations.append("평균 이상의 서비스를 제공하는 치과입니다")
        
        # 강점 분석
        strengths = []
        if recommendation['price_competitiveness'] >= 75:
            strengths.append("가격이 합리적")
        if recommendation['medical_skill'] >= 75:
            strengths.append("의료진 실력이 우수")
        if recommendation['overtreatment_risk'] <= 25:
            strengths.append("과잉진료 위험이 낮음")
        if recommendation['patient_satisfaction'] >= 75:
            strengths.append("환자 만족도가 높음")
        
        if strengths:
            explanations.append(f"특히 {', '.join(strengths)}으로 평가받고 있습니다")
        
        # 시설 정보
        facilities = []
        if recommendation['has_parking']:
            facilities.append("주차 가능")
        if recommendation['night_service']:
            facilities.append("야간 진료")
        if recommendation['weekend_service']:
            facilities.append("주말 진료")
        
        if facilities:
            explanations.append(f"{', '.join(facilities)} 서비스를 제공합니다")
        
        # 리뷰 수 정보
        review_count = recommendation['review_count']
        if review_count >= 50:
            explanations.append(f"풍부한 리뷰 데이터({review_count}개)를 바탕으로 분석되었습니다")
        
        return ". ".join(explanations) + "."
    
    def _generate_cache_key(
        self, 
        district: str, 
        treatment_type: Optional[str], 
        limit: int
    ) -> str:
        """
        캐시 키 생성
        """
        treatment_part = f"_{treatment_type}" if treatment_type else ""
        return f"recommendations_{district}{treatment_part}_{limit}_{self.ALGORITHM_VERSION}"
    
    def log_recommendation(
        self,
        user,
        district: str,
        treatment_type: Optional[str],
        recommendations: List[Dict],
        response_time_ms: int,
        request_ip: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> RecommendationLog:
        """
        추천 로그 저장
        """
        return RecommendationLog.objects.create(
            user=user,
            district=district,
            treatment_type=treatment_type,
            recommended_clinics=recommendations,
            algorithm_version=self.ALGORITHM_VERSION,
            response_time_ms=response_time_ms,
            request_ip=request_ip,
            user_agent=user_agent
        )


# 싱글톤 인스턴스
recommendation_engine = RecommendationEngine()