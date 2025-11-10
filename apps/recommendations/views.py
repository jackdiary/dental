"""
추천 시스템 API 뷰
"""
import time
import logging
from typing import Optional
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle
from rest_framework.views import APIView

from .services import recommendation_engine
from .utils import LocationUtils, RecommendationValidator
from .serializers import RecommendationRequestSerializer, RecommendationResponseSerializer

logger = logging.getLogger(__name__)


class RecommendationRateThrottle(UserRateThrottle):
    """
    추천 API 요청 제한 (시간당 100회)
    """
    scope = 'recommendation'
    rate = '100/hour'


class RecommendationAPIView(APIView):
    """
    치과 추천 API
    """
    throttle_classes = [RecommendationRateThrottle]
    
    def post(self, request):
        """
        치과 추천 요청 처리
        
        POST /api/recommend/
        {
            "district": "강남구",
            "treatment_type": "스케일링",  // 선택적
            "user_location": {  // 선택적
                "latitude": 37.5173,
                "longitude": 127.0473
            },
            "limit": 10  // 선택적, 기본값 10
        }
        """
        start_time = time.time()
        
        try:
            # 요청 데이터 검증
            serializer = RecommendationRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'error': '입력 데이터가 올바르지 않습니다',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            validated_data = serializer.validated_data
            
            # 파라미터 추출
            district = validated_data['district']
            treatment_type = validated_data.get('treatment_type')
            limit = validated_data.get('limit', 10)
            
            # 사용자 위치 처리
            user_location = None
            if 'user_location' in validated_data:
                loc_data = validated_data['user_location']
                user_location = (loc_data['latitude'], loc_data['longitude'])
            
            # 추천 실행
            recommendations = recommendation_engine.get_recommendations(
                district=district,
                treatment_type=treatment_type,
                user_location=user_location,
                limit=limit
            )
            
            # 결과 검증
            recommendations = RecommendationValidator.filter_valid_recommendations(recommendations)
            
            # 응답 시간 계산
            response_time_ms = int((time.time() - start_time) * 1000)
            
            # 추천 로그 저장
            try:
                recommendation_engine.log_recommendation(
                    user=request.user if request.user.is_authenticated else None,
                    district=district,
                    treatment_type=treatment_type,
                    recommendations=recommendations,
                    response_time_ms=response_time_ms,
                    request_ip=self._get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Exception as e:
                logger.warning(f"추천 로그 저장 실패: {e}")
            
            # 응답 데이터 구성
            response_data = {
                'success': True,
                'recommendations': recommendations,
                'metadata': {
                    'district': district,
                    'treatment_type': treatment_type,
                    'total_count': len(recommendations),
                    'response_time_ms': response_time_ms,
                    'algorithm_version': recommendation_engine.ALGORITHM_VERSION
                }
            }
            
            # 응답 시간 검증 (3초 이내)
            if response_time_ms > 3000:
                logger.warning(f"응답 시간 초과: {response_time_ms}ms")
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"추천 API 오류: {e}", exc_info=True)
            
            response_time_ms = int((time.time() - start_time) * 1000)
            
            return Response({
                'success': False,
                'error': '추천 처리 중 오류가 발생했습니다',
                'metadata': {
                    'response_time_ms': response_time_ms
                }
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _get_client_ip(self, request):
        """
        클라이언트 IP 주소 추출
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ClinicDetailAPIView(APIView):
    """
    치과 상세 정보 API
    """
    
    def get(self, request, clinic_id):
        """
        치과 상세 정보 조회
        
        GET /api/clinics/{clinic_id}/
        """
        try:
            from apps.clinics.models import Clinic
            from apps.clinics.serializers import ClinicDetailSerializer
            
            clinic = Clinic.objects.get(id=clinic_id)
            serializer = ClinicDetailSerializer(clinic)
            
            return Response({
                'success': True,
                'clinic': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Clinic.DoesNotExist:
            return Response({
                'success': False,
                'error': '치과를 찾을 수 없습니다'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"치과 상세 조회 오류: {e}")
            return Response({
                'success': False,
                'error': '치과 정보 조회 중 오류가 발생했습니다'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PriceComparisonAPIView(APIView):
    """
    가격 비교 API
    """
    
    def get(self, request):
        """
        지역별 치료 가격 비교
        
        GET /api/prices/compare/?district=강남구&treatment=스케일링
        """
        try:
            from .utils import PriceAnalyzer
            
            district = request.GET.get('district')
            treatment_type = request.GET.get('treatment')
            
            if not district or not treatment_type:
                return Response({
                    'success': False,
                    'error': 'district와 treatment 파라미터가 필요합니다'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # 가격 통계 조회
            price_stats = PriceAnalyzer.get_regional_price_stats(district, treatment_type)
            
            if not price_stats.get('count'):
                return Response({
                    'success': False,
                    'error': '해당 지역의 가격 데이터가 없습니다'
                }, status=status.HTTP_404_NOT_FOUND)
            
            return Response({
                'success': True,
                'price_comparison': {
                    'district': district,
                    'treatment_type': treatment_type,
                    'statistics': price_stats,
                    'price_levels': {
                        'low': f"{price_stats.get('q1', 0):,}원 이하",
                        'average': f"{price_stats.get('q1', 0):,}원 ~ {price_stats.get('q3', 0):,}원",
                        'high': f"{price_stats.get('q3', 0):,}원 이상"
                    }
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"가격 비교 API 오류: {e}")
            return Response({
                'success': False,
                'error': '가격 비교 중 오류가 발생했습니다'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def trigger_crawling(request):
    """
    관리자용 크롤링 트리거 API
    
    POST /api/admin/crawl/
    {
        "clinic_ids": [1, 2, 3],  // 선택적
        "source": "naver"  // 선택적: "naver", "google", "all"
    }
    """
    try:
        # 관리자 권한 확인
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': '관리자 권한이 필요합니다'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from tasks.crawling import crawl_all_sources, crawl_naver_reviews, crawl_google_reviews
        
        clinic_ids = request.data.get('clinic_ids', [])
        source = request.data.get('source', 'all')
        
        # Celery 태스크 실행
        if source == 'naver':
            task = crawl_naver_reviews.delay(clinic_ids)
        elif source == 'google':
            task = crawl_google_reviews.delay(clinic_ids)
        else:
            task = crawl_all_sources.delay(clinic_ids)
        
        return Response({
            'success': True,
            'message': '크롤링이 시작되었습니다',
            'task_id': task.id,
            'source': source,
            'clinic_count': len(clinic_ids) if clinic_ids else 'all'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"크롤링 트리거 오류: {e}")
        return Response({
            'success': False,
            'error': '크롤링 시작 중 오류가 발생했습니다'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def crawling_status(request, task_id):
    """
    크롤링 상태 조회 API
    
    GET /api/admin/crawl/{task_id}/status/
    """
    try:
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': '관리자 권한이 필요합니다'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from celery.result import AsyncResult
        
        result = AsyncResult(task_id)
        
        return Response({
            'success': True,
            'task_id': task_id,
            'status': result.status,
            'result': result.result if result.ready() else None,
            'info': result.info
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"크롤링 상태 조회 오류: {e}")
        return Response({
            'success': False,
            'error': '상태 조회 중 오류가 발생했습니다'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RecommendationFeedbackAPIView(APIView):
    """
    추천 피드백 API
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        추천 피드백 제출
        
        POST /api/recommendations/feedback/
        {
            "recommendation_log_id": 123,
            "clinic_id": 456,
            "feedback_type": "helpful",
            "comment": "정말 도움이 되었습니다",
            "did_visit": true,
            "visit_rating": 5
        }
        """
        try:
            from .models import RecommendationFeedback, RecommendationLog
            from apps.clinics.models import Clinic
            
            data = request.data
            
            # 필수 필드 확인
            required_fields = ['recommendation_log_id', 'clinic_id', 'feedback_type']
            for field in required_fields:
                if field not in data:
                    return Response({
                        'success': False,
                        'error': f'{field} 필드가 필요합니다'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # 추천 로그 확인
            try:
                recommendation_log = RecommendationLog.objects.get(
                    id=data['recommendation_log_id'],
                    user=request.user
                )
            except RecommendationLog.DoesNotExist:
                return Response({
                    'success': False,
                    'error': '추천 로그를 찾을 수 없습니다'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 치과 확인
            try:
                clinic = Clinic.objects.get(id=data['clinic_id'])
            except Clinic.DoesNotExist:
                return Response({
                    'success': False,
                    'error': '치과를 찾을 수 없습니다'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # 피드백 생성 또는 업데이트
            feedback, created = RecommendationFeedback.objects.update_or_create(
                recommendation_log=recommendation_log,
                clinic=clinic,
                defaults={
                    'feedback_type': data['feedback_type'],
                    'comment': data.get('comment', ''),
                    'did_visit': data.get('did_visit'),
                    'visit_rating': data.get('visit_rating')
                }
            )
            
            return Response({
                'success': True,
                'message': '피드백이 저장되었습니다',
                'feedback_id': feedback.id,
                'created': created
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"피드백 저장 오류: {e}")
            return Response({
                'success': False,
                'error': '피드백 저장 중 오류가 발생했습니다'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def system_status(request):
    """
    시스템 상태 모니터링 API
    
    GET /api/admin/system/status/
    """
    try:
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': '관리자 권한이 필요합니다'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from .monitoring import system_monitor
        
        status_data = system_monitor.get_system_status()
        
        return Response({
            'success': True,
            'system_status': status_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"시스템 상태 조회 오류: {e}")
        return Response({
            'success': False,
            'error': '시스템 상태 조회 중 오류가 발생했습니다'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def ml_model_metrics(request):
    """
    ML 모델 성능 지표 API
    
    GET /api/admin/ml/metrics/
    """
    try:
        if not request.user.is_staff:
            return Response({
                'success': False,
                'error': '관리자 권한이 필요합니다'
            }, status=status.HTTP_403_FORBIDDEN)
        
        from .monitoring import system_monitor
        
        metrics = system_monitor.get_ml_model_metrics()
        
        return Response({
            'success': True,
            'ml_metrics': metrics
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"ML 모델 지표 조회 오류: {e}")
        return Response({
            'success': False,
            'error': 'ML 모델 지표 조회 중 오류가 발생했습니다'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)