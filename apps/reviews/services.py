"""
리뷰 관련 서비스 로직
"""
from typing import List, Dict, Optional
from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Review
from .crawlers.base import crawler_manager
from apps.clinics.models import Clinic
import logging

logger = logging.getLogger(__name__)


class ReviewService:
    """리뷰 관련 비즈니스 로직"""
    
    @staticmethod
    def get_clinic_reviews(clinic_id: int, source: Optional[str] = None, 
                          processed_only: bool = True) -> List[Review]:
        """치과의 리뷰 조회"""
        queryset = Review.objects.filter(clinic_id=clinic_id)
        
        if source:
            queryset = queryset.filter(source=source)
        
        if processed_only:
            queryset = queryset.filter(is_processed=True, is_duplicate=False, is_flagged=False)
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_review_statistics(clinic_id: int) -> Dict:
        """치과 리뷰 통계 조회"""
        reviews = Review.objects.filter(
            clinic_id=clinic_id,
            is_processed=True,
            is_duplicate=False,
            is_flagged=False
        )
        
        stats = reviews.aggregate(
            total_count=Count('id'),
            avg_rating=Avg('original_rating'),
            naver_count=Count('id', filter=Q(source='naver')),
            google_count=Count('id', filter=Q(source='google'))
        )
        
        # 최근 30일 리뷰 수
        recent_date = timezone.now() - timedelta(days=30)
        recent_count = reviews.filter(created_at__gte=recent_date).count()
        
        return {
            'total_reviews': stats['total_count'] or 0,
            'average_rating': round(stats['avg_rating'] or 0, 2),
            'naver_reviews': stats['naver_count'] or 0,
            'google_reviews': stats['google_count'] or 0,
            'recent_reviews': recent_count,
            'last_updated': reviews.first().created_at if reviews.exists() else None
        }
    
    @staticmethod
    def mark_reviews_as_processed(review_ids: List[int]) -> int:
        """리뷰들을 처리 완료로 표시"""
        updated_count = Review.objects.filter(
            id__in=review_ids
        ).update(is_processed=True)
        
        logger.info(f"{updated_count}개 리뷰가 처리 완료로 표시됨")
        return updated_count
    
    @staticmethod
    def mark_reviews_as_duplicate(review_ids: List[int]) -> int:
        """리뷰들을 중복으로 표시"""
        updated_count = Review.objects.filter(
            id__in=review_ids
        ).update(is_duplicate=True)
        
        logger.info(f"{updated_count}개 리뷰가 중복으로 표시됨")
        return updated_count
    
    @staticmethod
    def flag_reviews(review_ids: List[int], reason: str = '') -> int:
        """리뷰들을 플래그 처리"""
        updated_count = Review.objects.filter(
            id__in=review_ids
        ).update(is_flagged=True)
        
        logger.info(f"{updated_count}개 리뷰가 플래그 처리됨: {reason}")
        return updated_count
    
    @staticmethod
    def search_reviews(query: str, clinic_id: Optional[int] = None) -> List[Review]:
        """리뷰 텍스트 검색"""
        queryset = Review.objects.filter(
            is_processed=True,
            is_duplicate=False,
            is_flagged=False
        )
        
        if clinic_id:
            queryset = queryset.filter(clinic_id=clinic_id)
        
        # PostgreSQL 전문 검색 사용
        if hasattr(Review, 'search_vector'):
            queryset = queryset.filter(search_vector=query)
        else:
            # 폴백: 일반 텍스트 검색
            queryset = queryset.filter(
                Q(original_text__icontains=query) | 
                Q(processed_text__icontains=query)
            )
        
        return queryset.order_by('-created_at')


class CrawlingService:
    """크롤링 관련 서비스"""
    
    @staticmethod
    def trigger_crawling(clinic_id: int, source: str, max_reviews: int = 100) -> Dict:
        """크롤링 트리거"""
        try:
            clinic = Clinic.objects.get(id=clinic_id)
            result = crawler_manager.crawl_clinic_reviews(clinic, source, max_reviews)
            
            # 치과 통계 업데이트
            clinic.update_review_stats()
            
            return result
            
        except Clinic.DoesNotExist:
            return {
                'status': 'error',
                'error_message': f'치과를 찾을 수 없습니다: {clinic_id}'
            }
        except Exception as e:
            logger.error(f"크롤링 트리거 실패: {e}")
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    @staticmethod
    def get_crawling_status(clinic_id: int) -> Dict:
        """크롤링 상태 조회"""
        try:
            clinic = Clinic.objects.get(id=clinic_id)
            
            # 최근 크롤링 정보
            recent_reviews = Review.objects.filter(
                clinic=clinic
            ).order_by('-created_at')[:10]
            
            # 소스별 통계
            from django.db.models import Max
            source_stats = Review.objects.filter(clinic=clinic).values('source').annotate(
                count=Count('id'),
                latest=Max('created_at')
            )
            
            return {
                'clinic_id': clinic_id,
                'clinic_name': clinic.name,
                'total_reviews': clinic.total_reviews,
                'recent_reviews': [
                    {
                        'id': r.id,
                        'source': r.source,
                        'created_at': r.created_at,
                        'is_processed': r.is_processed
                    } for r in recent_reviews
                ],
                'source_statistics': list(source_stats)
            }
            
        except Clinic.DoesNotExist:
            return {
                'status': 'error',
                'error_message': f'치과를 찾을 수 없습니다: {clinic_id}'
            }


class DuplicateDetectionService:
    """중복 리뷰 탐지 서비스"""
    
    @staticmethod
    def detect_duplicates(clinic_id: int, similarity_threshold: float = 0.8) -> List[Dict]:
        """중복 리뷰 탐지"""
        reviews = Review.objects.filter(
            clinic_id=clinic_id,
            is_duplicate=False
        ).order_by('created_at')
        
        duplicates = []
        processed_reviews = []
        
        for review in reviews:
            is_duplicate = False
            
            for processed_review in processed_reviews:
                # 간단한 텍스트 유사도 계산 (실제로는 더 정교한 알고리즘 사용)
                similarity = DuplicateDetectionService._calculate_similarity(
                    review.original_text, 
                    processed_review.original_text
                )
                
                if similarity >= similarity_threshold:
                    duplicates.append({
                        'original_review_id': processed_review.id,
                        'duplicate_review_id': review.id,
                        'similarity_score': similarity,
                        'original_text': processed_review.original_text[:100],
                        'duplicate_text': review.original_text[:100]
                    })
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                processed_reviews.append(review)
        
        return duplicates
    
    @staticmethod
    def _calculate_similarity(text1: str, text2: str) -> float:
        """텍스트 유사도 계산 (간단한 구현)"""
        if not text1 or not text2:
            return 0.0
        
        # 단어 집합 기반 Jaccard 유사도
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0
    
    @staticmethod
    def auto_mark_duplicates(clinic_id: int, similarity_threshold: float = 0.9) -> int:
        """자동 중복 리뷰 표시"""
        duplicates = DuplicateDetectionService.detect_duplicates(clinic_id, similarity_threshold)
        
        duplicate_ids = [dup['duplicate_review_id'] for dup in duplicates]
        
        if duplicate_ids:
            marked_count = ReviewService.mark_reviews_as_duplicate(duplicate_ids)
            logger.info(f"자동으로 {marked_count}개 리뷰가 중복으로 표시됨 (치과 ID: {clinic_id})")
            return marked_count
        
        return 0