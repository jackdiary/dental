"""
리뷰 관련 API 뷰
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
import logging

from apps.clinics.models import Clinic
from .services import CrawlingService, ReviewService
from .models import Review

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def trigger_crawling(request):
    """
    크롤링 트리거 API
    POST /api/reviews/crawl/
    """
    try:
        data = request.data
        clinic_id = data.get('clinic_id')
        source = data.get('source', 'naver')  # 기본값: naver
        max_reviews = data.get('max_reviews', 50)
        
        if not clinic_id:
            return Response({
                'error': 'clinic_id가 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 지원되는 소스 확인
        if source not in ['naver', 'google']:
            return Response({
                'error': '지원되는 소스: naver, google'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 크롤링 실행
        result = CrawlingService.trigger_crawling(clinic_id, source, max_reviews)
        
        if result.get('status') == 'error':
            return Response({
                'error': result.get('error_message', '크롤링 실패')
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'message': '크롤링이 성공적으로 완료되었습니다.',
            'result': result
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"크롤링 API 오류: {e}")
        return Response({
            'error': f'크롤링 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def crawling_status(request, clinic_id):
    """
    크롤링 상태 조회 API
    GET /api/reviews/status/<clinic_id>/
    """
    try:
        status_data = CrawlingService.get_crawling_status(clinic_id)
        
        if status_data.get('status') == 'error':
            return Response({
                'error': status_data.get('error_message', '상태 조회 실패')
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response(status_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"크롤링 상태 조회 오류: {e}")
        return Response({
            'error': f'상태 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([])
def clinic_reviews(request, clinic_id):
    """
    치과 리뷰 목록 조회 API
    GET /api/reviews/clinic/<clinic_id>/
    """
    try:
        # 치과 존재 확인
        clinic = get_object_or_404(Clinic, id=clinic_id)
        
        # 쿼리 파라미터
        source = request.GET.get('source')  # naver, google 또는 None (전체)
        processed_only = request.GET.get('processed_only', 'false').lower() == 'true'
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 20))
        
        # 리뷰 쿼리
        reviews_query = Review.objects.filter(clinic_id=clinic_id)
        
        if source:
            reviews_query = reviews_query.filter(source=source)
        
        if processed_only:
            reviews_query = reviews_query.filter(is_processed=True)
        
        # 최신순 정렬
        reviews_query = reviews_query.order_by('-created_at')
        
        # 전체 개수
        total_count = reviews_query.count()
        
        # 페이지네이션
        start = (page - 1) * page_size
        end = start + page_size
        paginated_reviews = reviews_query[start:end]
        
        # 리뷰 데이터 구성
        review_data = []
        for review in paginated_reviews:
            review_data.append({
                'id': review.id,
                'source': review.source,
                'text': review.original_text,
                'rating': review.original_rating,
                'review_date': review.review_date.isoformat() if review.review_date else None,
                'created_at': review.created_at.isoformat(),
                'is_processed': review.is_processed,
                'is_duplicate': review.is_duplicate,
                'is_flagged': review.is_flagged,
                'reviewer_hash': review.reviewer_hash[:8] if review.reviewer_hash else 'anonymous'
            })
        
        response_data = {
            'reviews': review_data,
            'total_count': total_count,
            'page': page,
            'page_size': page_size,
            'has_next': end < total_count,
            'clinic_name': clinic.name
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"리뷰 목록 조회 오류: {e}")
        return Response({
            'error': f'리뷰 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def review_statistics(request, clinic_id):
    """
    리뷰 통계 조회 API
    GET /api/reviews/statistics/<clinic_id>/
    """
    try:
        stats = ReviewService.get_review_statistics(clinic_id)
        return Response(stats, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"리뷰 통계 조회 오류: {e}")
        return Response({
            'error': f'통계 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def mark_reviews_processed(request):
    """
    리뷰 처리 완료 표시 API
    POST /api/reviews/mark-processed/
    """
    try:
        review_ids = request.data.get('review_ids', [])
        
        if not review_ids:
            return Response({
                'error': 'review_ids가 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = ReviewService.mark_reviews_as_processed(review_ids)
        
        return Response({
            'message': f'{updated_count}개 리뷰가 처리 완료로 표시되었습니다.',
            'updated_count': updated_count
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"리뷰 처리 표시 오류: {e}")
        return Response({
            'error': f'처리 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsAdminUser])
def flag_reviews(request):
    """
    리뷰 플래그 처리 API
    POST /api/reviews/flag/
    """
    try:
        review_ids = request.data.get('review_ids', [])
        reason = request.data.get('reason', '')
        
        if not review_ids:
            return Response({
                'error': 'review_ids가 필요합니다.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        updated_count = ReviewService.flag_reviews(review_ids, reason)
        
        return Response({
            'message': f'{updated_count}개 리뷰가 플래그 처리되었습니다.',
            'updated_count': updated_count,
            'reason': reason
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"리뷰 플래그 처리 오류: {e}")
        return Response({
            'error': f'처리 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class CrawlingTestView(View):
    """
    크롤링 테스트용 뷰 (개발용)
    """
    
    def post(self, request):
        """간단한 크롤링 테스트"""
        try:
            data = json.loads(request.body)
            clinic_id = data.get('clinic_id')
            source = data.get('source', 'naver')
            headless = data.get('headless', True)
            
            if not clinic_id:
                return JsonResponse({
                    'error': 'clinic_id가 필요합니다.'
                }, status=400)
            
            clinic = get_object_or_404(Clinic, id=clinic_id)
            
            # 테스트용 크롤링 (최대 5개 리뷰만)
            result = CrawlingService.trigger_crawling(clinic_id, source, max_reviews=5)
            
            return JsonResponse({
                'message': '테스트 크롤링 완료',
                'clinic_name': clinic.name,
                'result': result
            })
            
        except Exception as e:
            logger.error(f"크롤링 테스트 오류: {e}")
            return JsonResponse({
                'error': f'테스트 중 오류가 발생했습니다: {str(e)}'
            }, status=500)
    
    def get(self, request):
        """크롤링 가능한 치과 목록"""
        try:
            clinics = Clinic.objects.all()[:10]  # 최대 10개만
            
            clinic_list = []
            for clinic in clinics:
                clinic_list.append({
                    'id': clinic.id,
                    'name': clinic.name,
                    'district': clinic.district,
                    'address': clinic.address,
                    'total_reviews': clinic.total_reviews or 0
                })
            
            return JsonResponse({
                'clinics': clinic_list,
                'total_count': clinics.count()
            })
            
        except Exception as e:
            logger.error(f"치과 목록 조회 오류: {e}")
            return JsonResponse({
                'error': f'조회 중 오류가 발생했습니다: {str(e)}'
            }, status=500)