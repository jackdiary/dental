"""
리뷰 전처리 서비스
"""
from typing import List, Dict, Optional
from django.db import transaction
from django.utils import timezone
import logging
from .models import Review
from utils.nlp.preprocessing import (
    ReviewPreprocessingPipeline, 
    PreprocessingConfig,
    TextQualityAnalyzer
)
from utils.nlp.sentiment_analysis import analyze_review_sentiment
from apps.analysis.models import SentimentAnalysis

logger = logging.getLogger(__name__)


class ReviewPreprocessingService:
    """리뷰 전처리 서비스"""
    
    def __init__(self, config: Optional[PreprocessingConfig] = None):
        self.config = config or PreprocessingConfig()
        self.pipeline = ReviewPreprocessingPipeline(self.config)
    
    def process_unprocessed_reviews(self, clinic_id: Optional[int] = None, batch_size: int = 100) -> Dict:
        """처리되지 않은 리뷰들을 전처리"""
        try:
            # 처리되지 않은 리뷰 조회
            queryset = Review.objects.filter(
                is_processed=False,
                is_duplicate=False,
                is_flagged=False
            )
            
            if clinic_id:
                queryset = queryset.filter(clinic_id=clinic_id)
            
            unprocessed_reviews = queryset[:batch_size]
            
            if not unprocessed_reviews:
                return {
                    'status': 'success',
                    'message': '처리할 리뷰가 없습니다.',
                    'processed_count': 0
                }
            
            logger.info(f"전처리 시작: {len(unprocessed_reviews)}개 리뷰")
            
            # 텍스트 추출
            review_texts = [review.original_text for review in unprocessed_reviews]
            
            # 일괄 전처리
            preprocessed_results = self.pipeline.process_reviews(review_texts)
            
            # 결과 저장
            processed_count = self._save_preprocessing_results(
                unprocessed_reviews, 
                preprocessed_results
            )
            
            return {
                'status': 'success',
                'processed_count': processed_count,
                'total_reviews': len(unprocessed_reviews),
                'clinic_id': clinic_id
            }
            
        except Exception as e:
            logger.error(f"리뷰 전처리 실패: {e}")
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    def process_single_review(self, review_id: int) -> Dict:
        """단일 리뷰 전처리"""
        try:
            review = Review.objects.get(id=review_id)
            
            # 전처리 실행
            preprocessed = self.pipeline.preprocessor.preprocess_single(review.original_text)
            
            # 결과 저장
            self._update_review_with_preprocessing(review, preprocessed)
            
            return {
                'status': 'success',
                'review_id': review_id,
                'processed_text_length': len(preprocessed.processed_text),
                'keywords_count': len(preprocessed.keywords)
            }
            
        except Review.DoesNotExist:
            return {
                'status': 'error',
                'error_message': f'리뷰를 찾을 수 없습니다: {review_id}'
            }
        except Exception as e:
            logger.error(f"단일 리뷰 전처리 실패: {e}")
            return {
                'status': 'error',
                'error_message': str(e)
            }
    
    def _save_preprocessing_results(self, reviews: List[Review], results: List) -> int:
        """전처리 결과 저장"""
        processed_count = 0
        
        with transaction.atomic():
            for review, preprocessed in zip(reviews, results):
                try:
                    self._update_review_with_preprocessing(review, preprocessed)
                    processed_count += 1
                except Exception as e:
                    logger.error(f"리뷰 ID {review.id} 저장 실패: {e}")
        
        logger.info(f"전처리 결과 저장 완료: {processed_count}개")
        return processed_count
    
    def _update_review_with_preprocessing(self, review: Review, preprocessed) -> None:
        """리뷰에 전처리 결과 업데이트"""
        # 전처리된 텍스트 저장
        review.processed_text = preprocessed.processed_text
        
        # 품질 분석
        quality_scores = TextQualityAnalyzer.analyze_quality(review.original_text)
        
        # 저품질 리뷰는 플래그 처리
        if quality_scores['overall_score'] < 0.3:
            review.is_flagged = True
            logger.info(f"저품질 리뷰 플래그 처리: {review.id}")
        else:
            review.is_processed = True
            
            # 고품질 리뷰에 대해서만 감성 분석 수행
            try:
                self._perform_sentiment_analysis(review)
            except Exception as e:
                logger.error(f"감성 분석 실패 (리뷰 ID: {review.id}): {e}")
        
        # 검색 벡터 업데이트
        review.update_search_vector()
        
        review.save(update_fields=['processed_text', 'is_processed', 'is_flagged', 'search_vector'])
    
    def _perform_sentiment_analysis(self, review: Review) -> None:
        """감성 분석 수행 및 저장"""
        try:
            # 감성 분석 실행
            sentiment_result = analyze_review_sentiment(review.original_text)
            
            # 기존 감성 분석 결과가 있으면 업데이트, 없으면 생성
            sentiment_analysis, created = SentimentAnalysis.objects.get_or_create(
                review=review,
                defaults={
                    'price_score': sentiment_result.aspect_scores.price_score,
                    'skill_score': sentiment_result.aspect_scores.skill_score,
                    'kindness_score': sentiment_result.aspect_scores.kindness_score,
                    'waiting_time_score': sentiment_result.aspect_scores.waiting_time_score,
                    'facility_score': sentiment_result.aspect_scores.facility_score,
                    'overtreatment_score': sentiment_result.aspect_scores.overtreatment_score,
                    'model_version': sentiment_result.model_version,
                    'confidence_score': sentiment_result.confidence
                }
            )
            
            if not created:
                # 기존 결과 업데이트
                sentiment_analysis.price_score = sentiment_result.aspect_scores.price_score
                sentiment_analysis.skill_score = sentiment_result.aspect_scores.skill_score
                sentiment_analysis.kindness_score = sentiment_result.aspect_scores.kindness_score
                sentiment_analysis.waiting_time_score = sentiment_result.aspect_scores.waiting_time_score
                sentiment_analysis.facility_score = sentiment_result.aspect_scores.facility_score
                sentiment_analysis.overtreatment_score = sentiment_result.aspect_scores.overtreatment_score
                sentiment_analysis.model_version = sentiment_result.model_version
                sentiment_analysis.confidence_score = sentiment_result.confidence
                sentiment_analysis.save()
            
            logger.info(f"감성 분석 완료: 리뷰 ID {review.id}, 신뢰도 {sentiment_result.confidence:.2f}")
            
        except Exception as e:
            logger.error(f"감성 분석 저장 실패: {e}")
            raise
    
    def get_preprocessing_statistics(self, clinic_id: Optional[int] = None) -> Dict:
        """전처리 통계 조회"""
        queryset = Review.objects.all()
        
        if clinic_id:
            queryset = queryset.filter(clinic_id=clinic_id)
        
        stats = {
            'total_reviews': queryset.count(),
            'processed_reviews': queryset.filter(is_processed=True).count(),
            'unprocessed_reviews': queryset.filter(is_processed=False, is_duplicate=False, is_flagged=False).count(),
            'flagged_reviews': queryset.filter(is_flagged=True).count(),
            'duplicate_reviews': queryset.filter(is_duplicate=True).count()
        }
        
        # 처리율 계산
        if stats['total_reviews'] > 0:
            stats['processing_rate'] = (stats['processed_reviews'] / stats['total_reviews']) * 100
        else:
            stats['processing_rate'] = 0
        
        return stats
    
    def reprocess_reviews(self, review_ids: List[int]) -> Dict:
        """리뷰 재전처리"""
        try:
            reviews = Review.objects.filter(id__in=review_ids)
            
            if not reviews:
                return {
                    'status': 'error',
                    'error_message': '처리할 리뷰가 없습니다.'
                }
            
            # 상태 초기화
            reviews.update(
                processed_text='',
                is_processed=False,
                is_flagged=False
            )
            
            # 재전처리
            review_texts = [review.original_text for review in reviews]
            preprocessed_results = self.pipeline.process_reviews(review_texts)
            
            # 결과 저장
            processed_count = self._save_preprocessing_results(list(reviews), preprocessed_results)
            
            return {
                'status': 'success',
                'reprocessed_count': processed_count,
                'total_reviews': len(reviews)
            }
            
        except Exception as e:
            logger.error(f"리뷰 재전처리 실패: {e}")
            return {
                'status': 'error',
                'error_message': str(e)
            }


class ReviewQualityService:
    """리뷰 품질 관리 서비스"""
    
    @staticmethod
    def analyze_review_quality(review_id: int) -> Dict:
        """리뷰 품질 분석"""
        try:
            review = Review.objects.get(id=review_id)
            
            quality_scores = TextQualityAnalyzer.analyze_quality(review.original_text)
            
            return {
                'status': 'success',
                'review_id': review_id,
                'quality_scores': quality_scores,
                'is_high_quality': quality_scores['overall_score'] >= 0.6,
                'recommendations': ReviewQualityService._get_quality_recommendations(quality_scores)
            }
            
        except Review.DoesNotExist:
            return {
                'status': 'error',
                'error_message': f'리뷰를 찾을 수 없습니다: {review_id}'
            }
    
    @staticmethod
    def _get_quality_recommendations(quality_scores: Dict[str, float]) -> List[str]:
        """품질 개선 권장사항"""
        recommendations = []
        
        if quality_scores.get('length_score', 0) < 0.5:
            recommendations.append('리뷰 길이가 너무 짧거나 깁니다.')
        
        if quality_scores.get('korean_ratio_score', 0) < 0.5:
            recommendations.append('한글 비율이 낮습니다.')
        
        if quality_scores.get('special_char_score', 0) < 0.5:
            recommendations.append('특수문자가 너무 많습니다.')
        
        if quality_scores.get('repetition_score', 0) < 0.5:
            recommendations.append('반복되는 문자가 많습니다.')
        
        if quality_scores.get('meaningful_ratio_score', 0) < 0.5:
            recommendations.append('의미있는 단어 비율이 낮습니다.')
        
        return recommendations
    
    @staticmethod
    def get_low_quality_reviews(clinic_id: Optional[int] = None, limit: int = 50) -> List[Dict]:
        """저품질 리뷰 조회"""
        queryset = Review.objects.filter(is_processed=True)
        
        if clinic_id:
            queryset = queryset.filter(clinic_id=clinic_id)
        
        low_quality_reviews = []
        
        for review in queryset[:limit * 2]:  # 여유있게 조회
            quality_scores = TextQualityAnalyzer.analyze_quality(review.original_text)
            
            if quality_scores['overall_score'] < 0.4:  # 저품질 기준
                low_quality_reviews.append({
                    'review_id': review.id,
                    'clinic_name': review.clinic.name,
                    'text_preview': review.original_text[:100],
                    'quality_score': quality_scores['overall_score'],
                    'created_at': review.created_at
                })
                
                if len(low_quality_reviews) >= limit:
                    break
        
        return low_quality_reviews
    
    @staticmethod
    def auto_flag_low_quality_reviews(clinic_id: Optional[int] = None, threshold: float = 0.3) -> int:
        """저품질 리뷰 자동 플래그 처리"""
        queryset = Review.objects.filter(
            is_processed=True,
            is_flagged=False
        )
        
        if clinic_id:
            queryset = queryset.filter(clinic_id=clinic_id)
        
        flagged_count = 0
        
        for review in queryset:
            quality_scores = TextQualityAnalyzer.analyze_quality(review.original_text)
            
            if quality_scores['overall_score'] < threshold:
                review.is_flagged = True
                review.save(update_fields=['is_flagged'])
                flagged_count += 1
        
        logger.info(f"저품질 리뷰 자동 플래그 처리: {flagged_count}개")
        return flagged_count


# 전역 서비스 인스턴스
preprocessing_service = ReviewPreprocessingService()
quality_service = ReviewQualityService()