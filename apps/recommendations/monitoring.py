"""
시스템 모니터링 및 성능 지표 수집
"""
import time
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from django.core.cache import cache
from django.db.models import Avg, Count, Max, Min
from django.utils import timezone
from celery import current_app as celery_app

from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData
from .models import RecommendationLog, ClinicScore

logger = logging.getLogger(__name__)


class SystemMonitor:
    """
    시스템 상태 모니터링 클래스
    """
    
    def __init__(self):
        self.cache_timeout = 300  # 5분 캐시
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        전체 시스템 상태 반환
        """
        cache_key = "system_status"
        cached_status = cache.get(cache_key)
        
        if cached_status:
            return cached_status
        
        try:
            status = {
                'timestamp': timezone.now().isoformat(),
                'database': self._get_database_status(),
                'redis': self._get_redis_status(),
                'celery': self._get_celery_status(),
                'ml_models': self._get_ml_model_status(),
                'performance': self._get_performance_metrics(),
                'data_freshness': self._get_data_freshness(),
            }
            
            cache.set(cache_key, status, self.cache_timeout)
            return status
            
        except Exception as e:
            logger.error(f"시스템 상태 조회 오류: {e}")
            return {
                'timestamp': timezone.now().isoformat(),
                'error': str(e),
                'status': 'error'
            }
    
    def _get_database_status(self) -> Dict[str, Any]:
        """
        데이터베이스 상태 확인
        """
        try:
            # 기본 연결 테스트
            clinic_count = Clinic.objects.count()
            review_count = Review.objects.count()
            processed_reviews = Review.objects.filter(is_processed=True).count()
            sentiment_count = SentimentAnalysis.objects.count()
            price_count = PriceData.objects.count()
            
            return {
                'status': 'healthy',
                'total_clinics': clinic_count,
                'total_reviews': review_count,
                'processed_reviews': processed_reviews,
                'sentiment_analyses': sentiment_count,
                'price_data_points': price_count,
                'processing_rate': round((processed_reviews / review_count * 100) if review_count > 0 else 0, 2)
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _get_redis_status(self) -> Dict[str, Any]:
        """
        Redis 상태 확인
        """
        try:
            # Redis 연결 테스트
            cache.set('health_check', 'ok', 10)
            result = cache.get('health_check')
            
            if result == 'ok':
                # 캐시 히트율 계산 (추정)
                cache_hit_rate = self._estimate_cache_hit_rate()
                
                return {
                    'status': 'healthy',
                    'connection': 'ok',
                    'cache_hit_rate': cache_hit_rate
                }
            else:
                return {
                    'status': 'error',
                    'connection': 'failed'
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _get_celery_status(self) -> Dict[str, Any]:
        """
        Celery 상태 확인
        """
        try:
            # Celery 워커 상태 확인
            inspect = celery_app.control.inspect()
            
            # 활성 워커 확인
            active_workers = inspect.active()
            registered_tasks = inspect.registered()
            
            worker_count = len(active_workers) if active_workers else 0
            
            return {
                'status': 'healthy' if worker_count > 0 else 'warning',
                'active_workers': worker_count,
                'registered_tasks': len(registered_tasks) if registered_tasks else 0,
                'broker_url': str(celery_app.conf.broker_url).replace('redis://', 'redis://***')
            }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _get_ml_model_status(self) -> Dict[str, Any]:
        """
        ML 모델 상태 확인
        """
        try:
            # 최근 감성 분석 결과 확인
            recent_analyses = SentimentAnalysis.objects.filter(
                analyzed_at__gte=timezone.now() - timedelta(hours=24)
            )
            
            if recent_analyses.exists():
                avg_confidence = recent_analyses.aggregate(
                    avg_confidence=Avg('confidence_score')
                )['avg_confidence']
                
                model_versions = recent_analyses.values('model_version').distinct()
                
                return {
                    'status': 'healthy',
                    'recent_analyses_24h': recent_analyses.count(),
                    'average_confidence': round(float(avg_confidence), 3) if avg_confidence else 0,
                    'active_model_versions': [v['model_version'] for v in model_versions],
                    'last_analysis': recent_analyses.latest('analyzed_at').analyzed_at.isoformat()
                }
            else:
                return {
                    'status': 'warning',
                    'message': '최근 24시간 내 분석 결과 없음'
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """
        성능 지표 수집
        """
        try:
            # 최근 24시간 추천 로그 분석
            recent_logs = RecommendationLog.objects.filter(
                created_at__gte=timezone.now() - timedelta(hours=24)
            )
            
            if recent_logs.exists():
                response_times = recent_logs.exclude(
                    response_time_ms__isnull=True
                ).aggregate(
                    avg_response_time=Avg('response_time_ms'),
                    max_response_time=Max('response_time_ms'),
                    min_response_time=Min('response_time_ms')
                )
                
                total_requests = recent_logs.count()
                successful_requests = recent_logs.exclude(
                    recommended_clinics__isnull=True
                ).count()
                
                return {
                    'period': '24h',
                    'total_requests': total_requests,
                    'successful_requests': successful_requests,
                    'success_rate': round((successful_requests / total_requests * 100) if total_requests > 0 else 0, 2),
                    'avg_response_time_ms': round(response_times['avg_response_time'] or 0, 2),
                    'max_response_time_ms': response_times['max_response_time'] or 0,
                    'min_response_time_ms': response_times['min_response_time'] or 0
                }
            else:
                return {
                    'period': '24h',
                    'total_requests': 0,
                    'message': '최근 24시간 내 요청 없음'
                }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def _get_data_freshness(self) -> Dict[str, Any]:
        """
        데이터 신선도 확인
        """
        try:
            # 최신 리뷰 날짜
            latest_review = Review.objects.order_by('-created_at').first()
            
            # 최신 감성 분석 날짜
            latest_analysis = SentimentAnalysis.objects.order_by('-analyzed_at').first()
            
            # 최신 점수 계산 날짜
            latest_score = ClinicScore.objects.order_by('-last_calculated').first()
            
            now = timezone.now()
            
            result = {}
            
            if latest_review:
                hours_since_review = (now - latest_review.created_at).total_seconds() / 3600
                result['latest_review_hours_ago'] = round(hours_since_review, 1)
            
            if latest_analysis:
                hours_since_analysis = (now - latest_analysis.analyzed_at).total_seconds() / 3600
                result['latest_analysis_hours_ago'] = round(hours_since_analysis, 1)
            
            if latest_score:
                hours_since_score = (now - latest_score.last_calculated).total_seconds() / 3600
                result['latest_score_hours_ago'] = round(hours_since_score, 1)
            
            # 전체적인 데이터 신선도 평가
            max_hours = max([
                result.get('latest_review_hours_ago', 0),
                result.get('latest_analysis_hours_ago', 0),
                result.get('latest_score_hours_ago', 0)
            ])
            
            if max_hours <= 1:
                result['freshness_status'] = 'excellent'
            elif max_hours <= 6:
                result['freshness_status'] = 'good'
            elif max_hours <= 24:
                result['freshness_status'] = 'acceptable'
            else:
                result['freshness_status'] = 'stale'
            
            return result
            
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def _estimate_cache_hit_rate(self) -> float:
        """
        캐시 히트율 추정 (간단한 방법)
        """
        try:
            # 테스트 키들로 캐시 히트율 추정
            test_keys = [
                'recommendations_강남구_10_v1.0',
                'price_stats_강남구_스케일링',
                'system_status'
            ]
            
            hits = 0
            for key in test_keys:
                if cache.get(key) is not None:
                    hits += 1
            
            return round((hits / len(test_keys)) * 100, 2)
        except:
            return 0.0
    
    def get_ml_model_metrics(self) -> Dict[str, Any]:
        """
        ML 모델 성능 지표 수집
        """
        try:
            # 최근 1주일간의 감성 분석 결과
            week_ago = timezone.now() - timedelta(days=7)
            recent_analyses = SentimentAnalysis.objects.filter(
                analyzed_at__gte=week_ago
            )
            
            if not recent_analyses.exists():
                return {
                    'message': '최근 1주일 내 분석 결과 없음'
                }
            
            # 모델 버전별 통계
            model_stats = {}
            for analysis in recent_analyses:
                version = analysis.model_version
                if version not in model_stats:
                    model_stats[version] = {
                        'count': 0,
                        'confidence_scores': []
                    }
                
                model_stats[version]['count'] += 1
                model_stats[version]['confidence_scores'].append(float(analysis.confidence_score))
            
            # 각 모델 버전의 평균 신뢰도 계산
            for version, stats in model_stats.items():
                if stats['confidence_scores']:
                    stats['avg_confidence'] = sum(stats['confidence_scores']) / len(stats['confidence_scores'])
                    stats['min_confidence'] = min(stats['confidence_scores'])
                    stats['max_confidence'] = max(stats['confidence_scores'])
                    del stats['confidence_scores']  # 메모리 절약
            
            return {
                'period': '7 days',
                'total_analyses': recent_analyses.count(),
                'model_versions': model_stats,
                'overall_avg_confidence': round(
                    recent_analyses.aggregate(avg=Avg('confidence_score'))['avg'], 3
                )
            }
            
        except Exception as e:
            logger.error(f"ML 모델 지표 수집 오류: {e}")
            return {
                'error': str(e)
            }


# 싱글톤 인스턴스
system_monitor = SystemMonitor()