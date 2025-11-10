"""
기본 크롤러 인터페이스 및 유틸리티
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging
import time
import hashlib
from django.utils import timezone
from apps.clinics.models import Clinic
from apps.reviews.models import Review
from utils.text_processing import anonymize_personal_info, create_reviewer_hash, clean_text

logger = logging.getLogger(__name__)


@dataclass
class ReviewData:
    """크롤링된 리뷰 데이터 구조"""
    text: str
    rating: Optional[int] = None
    date: Optional[datetime] = None
    reviewer_name: Optional[str] = None
    external_id: Optional[str] = None
    metadata: Optional[Dict] = None


class BaseCrawler(ABC):
    """기본 크롤러 추상 클래스"""
    
    def __init__(self, delay_seconds: int = 2):
        self.delay_seconds = delay_seconds
        self.session_count = 0
        self.error_count = 0
        
    @abstractmethod
    def get_source_name(self) -> str:
        """크롤러 소스 이름 반환"""
        pass
    
    @abstractmethod
    def crawl_reviews(self, clinic: Clinic, max_reviews: int = 100) -> List[ReviewData]:
        """리뷰 크롤링 메인 메서드"""
        pass
    
    def save_reviews(self, clinic: Clinic, review_data_list: List[ReviewData]) -> Tuple[int, int]:
        """
        크롤링된 리뷰 데이터를 데이터베이스에 저장
        Returns: (저장된 리뷰 수, 중복 리뷰 수)
        """
        saved_count = 0
        duplicate_count = 0
        
        for review_data in review_data_list:
            try:
                # 개인정보 익명화
                cleaned_text = self.anonymize_review_text(review_data.text)
                
                # 중복 체크
                if self.is_duplicate_review(clinic, review_data):
                    duplicate_count += 1
                    continue
                
                # 리뷰 저장
                review = Review.objects.create(
                    clinic=clinic,
                    source=self.get_source_name(),
                    original_text=cleaned_text,
                    processed_text='',  # 나중에 전처리 단계에서 처리
                    original_rating=review_data.rating,
                    review_date=review_data.date or timezone.now(),
                    reviewer_hash=create_reviewer_hash(
                        review_data.reviewer_name or '', 
                        str(review_data.date) if review_data.date else ''
                    ),
                    external_id=review_data.external_id or '',
                    is_processed=False,
                    is_duplicate=False,
                    is_flagged=False
                )
                
                saved_count += 1
                logger.info(f"리뷰 저장 완료: {clinic.name} - {review.id}")
                
            except Exception as e:
                logger.error(f"리뷰 저장 실패: {clinic.name} - {e}")
                self.error_count += 1
        
        return saved_count, duplicate_count
    
    def anonymize_review_text(self, text: str) -> str:
        """리뷰 텍스트 개인정보 익명화"""
        if not text:
            return ''
        
        # 기본 텍스트 정제
        cleaned = clean_text(text)
        
        # 개인정보 익명화
        anonymized = anonymize_personal_info(cleaned)
        
        return anonymized
    
    def is_duplicate_review(self, clinic: Clinic, review_data: ReviewData) -> bool:
        """중복 리뷰 체크"""
        # external_id가 있는 경우 중복 체크
        if review_data.external_id:
            exists = Review.objects.filter(
                clinic=clinic,
                source=self.get_source_name(),
                external_id=review_data.external_id
            ).exists()
            if exists:
                return True
        
        # 텍스트 유사도 기반 중복 체크 (간단한 해시 비교)
        text_hash = hashlib.md5(review_data.text.encode('utf-8')).hexdigest()
        similar_reviews = Review.objects.filter(
            clinic=clinic,
            source=self.get_source_name()
        )
        
        for review in similar_reviews:
            existing_hash = hashlib.md5(review.original_text.encode('utf-8')).hexdigest()
            if text_hash == existing_hash:
                return True
        
        return False
    
    def add_delay(self):
        """크롤링 간 지연 시간 추가"""
        if self.delay_seconds > 0:
            time.sleep(self.delay_seconds)
    
    def log_crawling_stats(self, clinic: Clinic, total_reviews: int, saved_count: int, duplicate_count: int):
        """크롤링 통계 로깅"""
        logger.info(f"""
        크롤링 완료: {clinic.name}
        - 소스: {self.get_source_name()}
        - 수집된 리뷰: {total_reviews}개
        - 저장된 리뷰: {saved_count}개
        - 중복 리뷰: {duplicate_count}개
        - 오류 수: {self.error_count}개
        """)


class CrawlerManager:
    """크롤러 관리 클래스"""
    
    def __init__(self):
        self.crawlers = {}
    
    def register_crawler(self, source_name: str, crawler: BaseCrawler):
        """크롤러 등록"""
        self.crawlers[source_name] = crawler
    
    def get_crawler(self, source_name: str) -> Optional[BaseCrawler]:
        """크롤러 조회"""
        return self.crawlers.get(source_name)
    
    def crawl_clinic_reviews(self, clinic: Clinic, source_name: str, max_reviews: int = 100) -> Dict:
        """특정 치과의 리뷰 크롤링"""
        crawler = self.get_crawler(source_name)
        if not crawler:
            raise ValueError(f"크롤러를 찾을 수 없습니다: {source_name}")
        
        try:
            # 리뷰 크롤링
            review_data_list = crawler.crawl_reviews(clinic, max_reviews)
            
            # 리뷰 저장
            saved_count, duplicate_count = crawler.save_reviews(clinic, review_data_list)
            
            # 통계 로깅
            crawler.log_crawling_stats(clinic, len(review_data_list), saved_count, duplicate_count)
            
            return {
                'status': 'success',
                'clinic_id': clinic.id,
                'source': source_name,
                'total_reviews': len(review_data_list),
                'saved_reviews': saved_count,
                'duplicate_reviews': duplicate_count,
                'error_count': crawler.error_count
            }
            
        except Exception as e:
            logger.error(f"크롤링 실패: {clinic.name} ({source_name}) - {e}")
            return {
                'status': 'error',
                'clinic_id': clinic.id,
                'source': source_name,
                'error_message': str(e)
            }
    
    def crawl_all_sources(self, clinic: Clinic, max_reviews_per_source: int = 100) -> List[Dict]:
        """모든 소스에서 리뷰 크롤링"""
        results = []
        
        for source_name in self.crawlers.keys():
            result = self.crawl_clinic_reviews(clinic, source_name, max_reviews_per_source)
            results.append(result)
            
            # 소스 간 지연
            time.sleep(5)
        
        return results


# 전역 크롤러 매니저 인스턴스
crawler_manager = CrawlerManager()