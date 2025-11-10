"""
Celery tasks for review crawling
"""
from celery import shared_task
from django.utils import timezone
from django.db import transaction
import logging
from apps.clinics.models import Clinic
from apps.reviews.services import CrawlingService, DuplicateDetectionService
from apps.reviews.crawlers.base import crawler_manager

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def crawl_naver_reviews(self, clinic_id, max_reviews=100):
    """
    네이버 플레이스 리뷰 크롤링 태스크
    """
    try:
        logger.info(f"네이버 리뷰 크롤링 시작: 치과 ID {clinic_id}")
        
        # 크롤링 실행
        result = CrawlingService.trigger_crawling(clinic_id, 'naver', max_reviews)
        
        if result['status'] == 'success':
            # 중복 리뷰 자동 탐지 및 처리
            duplicate_count = DuplicateDetectionService.auto_mark_duplicates(clinic_id)
            result['auto_marked_duplicates'] = duplicate_count
            
            logger.info(f"네이버 리뷰 크롤링 완료: 치과 ID {clinic_id}, 수집 {result.get('saved_reviews', 0)}개")
        
        return result
        
    except Exception as exc:
        logger.error(f"네이버 리뷰 크롤링 실패: 치과 ID {clinic_id} - {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True)
def crawl_google_reviews(self, clinic_id, max_reviews=100):
    """
    구글 맵 리뷰 크롤링 태스크
    """
    try:
        logger.info(f"구글 리뷰 크롤링 시작: 치과 ID {clinic_id}")
        
        # 크롤링 실행
        result = CrawlingService.trigger_crawling(clinic_id, 'google', max_reviews)
        
        if result['status'] == 'success':
            # 중복 리뷰 자동 탐지 및 처리
            duplicate_count = DuplicateDetectionService.auto_mark_duplicates(clinic_id)
            result['auto_marked_duplicates'] = duplicate_count
            
            logger.info(f"구글 리뷰 크롤링 완료: 치과 ID {clinic_id}, 수집 {result.get('saved_reviews', 0)}개")
        
        return result
        
    except Exception as exc:
        logger.error(f"구글 리뷰 크롤링 실패: 치과 ID {clinic_id} - {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=3)


@shared_task(bind=True)
def crawl_all_sources(self, clinic_id, max_reviews_per_source=100):
    """
    모든 소스에서 리뷰 크롤링 태스크
    """
    try:
        logger.info(f"전체 소스 리뷰 크롤링 시작: 치과 ID {clinic_id}")
        
        clinic = Clinic.objects.get(id=clinic_id)
        results = crawler_manager.crawl_all_sources(clinic, max_reviews_per_source)
        
        # 전체 결과 집계
        total_saved = sum(r.get('saved_reviews', 0) for r in results if r.get('status') == 'success')
        total_duplicates = sum(r.get('duplicate_reviews', 0) for r in results if r.get('status') == 'success')
        
        # 중복 리뷰 자동 탐지 및 처리
        auto_marked_duplicates = DuplicateDetectionService.auto_mark_duplicates(clinic_id)
        
        summary = {
            'status': 'success',
            'clinic_id': clinic_id,
            'clinic_name': clinic.name,
            'total_saved_reviews': total_saved,
            'total_duplicate_reviews': total_duplicates,
            'auto_marked_duplicates': auto_marked_duplicates,
            'source_results': results
        }
        
        logger.info(f"전체 소스 리뷰 크롤링 완료: 치과 ID {clinic_id}, 총 수집 {total_saved}개")
        
        return summary
        
    except Clinic.DoesNotExist:
        error_msg = f"치과를 찾을 수 없습니다: ID {clinic_id}"
        logger.error(error_msg)
        return {'status': 'error', 'error_message': error_msg}
    
    except Exception as exc:
        logger.error(f"전체 소스 리뷰 크롤링 실패: 치과 ID {clinic_id} - {exc}")
        raise self.retry(exc=exc, countdown=120, max_retries=2)


@shared_task(bind=True)
def batch_crawl_clinics(self, clinic_ids, source='all', max_reviews=50):
    """
    여러 치과의 리뷰를 일괄 크롤링하는 태스크
    """
    try:
        logger.info(f"일괄 크롤링 시작: {len(clinic_ids)}개 치과, 소스: {source}")
        
        results = []
        
        for clinic_id in clinic_ids:
            try:
                if source == 'all':
                    result = crawl_all_sources.delay(clinic_id, max_reviews)
                elif source == 'naver':
                    result = crawl_naver_reviews.delay(clinic_id, max_reviews)
                elif source == 'google':
                    result = crawl_google_reviews.delay(clinic_id, max_reviews)
                else:
                    continue
                
                results.append({
                    'clinic_id': clinic_id,
                    'task_id': result.id,
                    'status': 'queued'
                })
                
            except Exception as e:
                logger.error(f"치과 ID {clinic_id} 크롤링 큐 추가 실패: {e}")
                results.append({
                    'clinic_id': clinic_id,
                    'status': 'error',
                    'error_message': str(e)
                })
        
        summary = {
            'status': 'success',
            'total_clinics': len(clinic_ids),
            'queued_tasks': len([r for r in results if r['status'] == 'queued']),
            'failed_tasks': len([r for r in results if r['status'] == 'error']),
            'results': results
        }
        
        logger.info(f"일괄 크롤링 큐 등록 완료: {summary['queued_tasks']}/{summary['total_clinics']}개")
        
        return summary
        
    except Exception as exc:
        logger.error(f"일괄 크롤링 실패: {exc}")
        raise self.retry(exc=exc, countdown=60, max_retries=2)


@shared_task
def cleanup_old_crawling_logs():
    """
    오래된 크롤링 로그 정리 태스크 (주기적 실행)
    """
    try:
        from datetime import timedelta
        from apps.reviews.models import Review
        
        # 30일 이전의 플래그된 리뷰 삭제
        cutoff_date = timezone.now() - timedelta(days=30)
        
        deleted_count = Review.objects.filter(
            is_flagged=True,
            created_at__lt=cutoff_date
        ).delete()[0]
        
        logger.info(f"오래된 플래그 리뷰 {deleted_count}개 삭제 완료")
        
        return {
            'status': 'success',
            'deleted_reviews': deleted_count,
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"크롤링 로그 정리 실패: {e}")
        return {
            'status': 'error',
            'error_message': str(e)
        }


@shared_task(bind=True)
def update_clinic_search_vectors(self):
    """
    모든 치과의 검색 벡터 업데이트 태스크
    """
    try:
        clinics = Clinic.objects.all()
        updated_count = 0
        
        for clinic in clinics:
            try:
                clinic.update_search_vector()
                updated_count += 1
            except Exception as e:
                logger.error(f"치과 ID {clinic.id} 검색 벡터 업데이트 실패: {e}")
        
        logger.info(f"검색 벡터 업데이트 완료: {updated_count}/{clinics.count()}개")
        
        return {
            'status': 'success',
            'total_clinics': clinics.count(),
            'updated_clinics': updated_count
        }
        
    except Exception as exc:
        logger.error(f"검색 벡터 업데이트 실패: {exc}")
        raise self.retry(exc=exc, countdown=300, max_retries=2)