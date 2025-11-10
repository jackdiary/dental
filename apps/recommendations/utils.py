"""
추천 시스템 유틸리티 함수들
"""
import logging
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from django.db.models import Avg, Count, Q, Min, Max
from django.core.cache import cache
from django.db import models

from apps.clinics.models import Clinic
from apps.analysis.models import PriceData

logger = logging.getLogger(__name__)


class LocationUtils:
    """
    위치 관련 유틸리티
    """
    
    @staticmethod
    def get_district_center(district: str) -> Optional[Tuple[float, float]]:
        """
        지역구의 중심 좌표 반환
        """
        # 주요 지역구 중심 좌표 (서울 기준)
        district_centers = {
            '강남구': (37.5173, 127.0473),
            '강동구': (37.5301, 127.1238),
            '강북구': (37.6398, 127.0256),
            '강서구': (37.5509, 126.8495),
            '관악구': (37.4784, 126.9516),
            '광진구': (37.5384, 127.0822),
            '구로구': (37.4955, 126.8876),
            '금천구': (37.4569, 126.8955),
            '노원구': (37.6544, 127.0565),
            '도봉구': (37.6688, 127.0471),
            '동대문구': (37.5744, 127.0396),
            '동작구': (37.5124, 126.9393),
            '마포구': (37.5663, 126.9019),
            '서대문구': (37.5791, 126.9368),
            '서초구': (37.4837, 127.0324),
            '성동구': (37.5634, 127.0365),
            '성북구': (37.5894, 127.0167),
            '송파구': (37.5145, 127.1059),
            '양천구': (37.5169, 126.8664),
            '영등포구': (37.5264, 126.8962),
            '용산구': (37.5384, 126.9654),
            '은평구': (37.6176, 126.9227),
            '종로구': (37.5735, 126.9788),
            '중구': (37.5640, 126.9970),
            '중랑구': (37.6063, 127.0925),
        }
        
        # 정확한 매칭 시도
        if district in district_centers:
            return district_centers[district]
        
        # 부분 매칭 시도
        for key, coords in district_centers.items():
            if district in key or key in district:
                return coords
        
        return None
    
    @staticmethod
    def calculate_distance_score(distance_km: float) -> float:
        """
        거리 기반 점수 계산 (가까울수록 높은 점수)
        """
        if distance_km <= 1:
            return 100.0
        elif distance_km <= 2:
            return 90.0
        elif distance_km <= 3:
            return 80.0
        elif distance_km <= 4:
            return 70.0
        elif distance_km <= 5:
            return 60.0
        else:
            return 50.0


class PriceAnalyzer:
    """
    가격 분석 유틸리티
    """
    
    @staticmethod
    def get_regional_price_stats(district: str, treatment_type: str) -> Dict:
        """
        지역별 치료 가격 통계 반환
        """
        cache_key = f"price_stats_{district}_{treatment_type}"
        cached_stats = cache.get(cache_key)
        
        if cached_stats:
            return cached_stats
        
        try:
            price_data = PriceData.objects.filter(
                clinic__district__icontains=district,
                treatment_type__icontains=treatment_type
            ).aggregate(
                avg_price=Avg('price'),
                min_price=models.Min('price'),
                max_price=models.Max('price'),
                count=Count('id')
            )
            
            # 가격 분포 계산
            prices = list(PriceData.objects.filter(
                clinic__district__icontains=district,
                treatment_type__icontains=treatment_type
            ).values_list('price', flat=True))
            
            if prices:
                prices.sort()
                n = len(prices)
                
                stats = {
                    'average': price_data['avg_price'],
                    'minimum': price_data['min_price'],
                    'maximum': price_data['max_price'],
                    'median': prices[n // 2] if n % 2 == 1 else (prices[n // 2 - 1] + prices[n // 2]) / 2,
                    'q1': prices[n // 4],
                    'q3': prices[3 * n // 4],
                    'count': price_data['count'],
                    'std_dev': PriceAnalyzer._calculate_std_dev(prices, price_data['avg_price'])
                }
            else:
                stats = {
                    'average': None,
                    'minimum': None,
                    'maximum': None,
                    'median': None,
                    'q1': None,
                    'q3': None,
                    'count': 0,
                    'std_dev': None
                }
            
            # 1시간 캐시
            cache.set(cache_key, stats, 3600)
            return stats
            
        except Exception as e:
            logger.error(f"가격 통계 계산 오류: {e}")
            return {}
    
    @staticmethod
    def _calculate_std_dev(prices: List[int], mean: float) -> float:
        """
        표준편차 계산
        """
        if not prices or mean is None:
            return 0.0
        
        variance = sum((price - mean) ** 2 for price in prices) / len(prices)
        return variance ** 0.5
    
    @staticmethod
    def classify_price_level(price: int, stats: Dict) -> str:
        """
        가격 수준 분류
        """
        if not stats.get('average'):
            return 'unknown'
        
        avg = stats['average']
        std_dev = stats.get('std_dev', 0)
        
        if price < avg - std_dev:
            return 'low'
        elif price > avg + std_dev:
            return 'high'
        else:
            return 'average'
    
    @staticmethod
    def get_price_competitiveness_score(clinic: Clinic, treatment_type: str) -> float:
        """
        가격 경쟁력 점수 계산
        """
        try:
            # 해당 치과의 평균 가격
            clinic_prices = PriceData.objects.filter(
                clinic=clinic,
                treatment_type__icontains=treatment_type
            )
            
            if not clinic_prices.exists():
                return 50.0  # 데이터 없음
            
            clinic_avg = clinic_prices.aggregate(avg=Avg('price'))['avg']
            
            # 지역 통계
            regional_stats = PriceAnalyzer.get_regional_price_stats(
                clinic.district, treatment_type
            )
            
            if not regional_stats.get('average'):
                return 50.0
            
            regional_avg = regional_stats['average']
            price_ratio = clinic_avg / regional_avg
            
            # 점수 계산 (저렴할수록 높은 점수)
            if price_ratio <= 0.8:  # 20% 이상 저렴
                return 95.0
            elif price_ratio <= 0.9:  # 10% 이상 저렴
                return 85.0
            elif price_ratio <= 1.1:  # 평균 수준
                return 70.0
            elif price_ratio <= 1.2:  # 20% 이상 비쌈
                return 50.0
            elif price_ratio <= 1.3:  # 30% 이상 비쌈
                return 30.0
            else:  # 30% 초과 비쌈
                return 10.0
                
        except Exception as e:
            logger.error(f"가격 경쟁력 계산 오류: {e}")
            return 50.0


class RecommendationValidator:
    """
    추천 결과 검증 유틸리티
    """
    
    @staticmethod
    def validate_recommendation_data(recommendation: Dict) -> bool:
        """
        추천 데이터 유효성 검증
        """
        required_fields = [
            'clinic_id', 'clinic_name', 'comprehensive_score',
            'price_competitiveness', 'medical_skill', 
            'overtreatment_risk', 'patient_satisfaction'
        ]
        
        # 필수 필드 확인
        for field in required_fields:
            if field not in recommendation:
                logger.warning(f"추천 데이터에 필수 필드 누락: {field}")
                return False
        
        # 점수 범위 확인
        score_fields = [
            'comprehensive_score', 'price_competitiveness', 
            'medical_skill', 'overtreatment_risk', 'patient_satisfaction'
        ]
        
        for field in score_fields:
            score = recommendation.get(field, 0)
            if not isinstance(score, (int, float)) or score < 0 or score > 100:
                logger.warning(f"점수 범위 오류 ({field}): {score}")
                return False
        
        return True
    
    @staticmethod
    def filter_valid_recommendations(recommendations: List[Dict]) -> List[Dict]:
        """
        유효한 추천만 필터링
        """
        valid_recommendations = []
        
        for rec in recommendations:
            if RecommendationValidator.validate_recommendation_data(rec):
                valid_recommendations.append(rec)
            else:
                logger.warning(f"유효하지 않은 추천 데이터 제외: {rec.get('clinic_name', 'Unknown')}")
        
        return valid_recommendations


class ScoreNormalizer:
    """
    점수 정규화 유틸리티
    """
    
    @staticmethod
    def normalize_to_percentile(scores: List[float]) -> List[float]:
        """
        점수를 백분위로 정규화
        """
        if not scores:
            return []
        
        sorted_scores = sorted(scores)
        n = len(sorted_scores)
        
        normalized = []
        for score in scores:
            rank = sorted_scores.index(score) + 1
            percentile = (rank / n) * 100
            normalized.append(percentile)
        
        return normalized
    
    @staticmethod
    def min_max_normalize(scores: List[float], target_min: float = 0, target_max: float = 100) -> List[float]:
        """
        Min-Max 정규화
        """
        if not scores:
            return []
        
        min_score = min(scores)
        max_score = max(scores)
        
        if min_score == max_score:
            return [target_min + (target_max - target_min) / 2] * len(scores)
        
        normalized = []
        for score in scores:
            normalized_score = target_min + (score - min_score) * (target_max - target_min) / (max_score - min_score)
            normalized.append(normalized_score)
        
        return normalized
    
    @staticmethod
    def z_score_normalize(scores: List[float]) -> List[float]:
        """
        Z-점수 정규화
        """
        if not scores:
            return []
        
        mean = sum(scores) / len(scores)
        variance = sum((score - mean) ** 2 for score in scores) / len(scores)
        std_dev = variance ** 0.5
        
        if std_dev == 0:
            return [0.0] * len(scores)
        
        return [(score - mean) / std_dev for score in scores]