#!/usr/bin/env python
"""
더미 데이터 삭제 스크립트
기존 테스트/더미 데이터를 삭제하고 실제 크롤링 데이터만 남깁니다.
"""
import os
import sys
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData
from apps.accounts.models import User
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_dummy_data():
    """더미 데이터 삭제"""
    logger.info("🧹 더미 데이터 삭제 시작")
    logger.info("=" * 60)
    
    # 현재 데이터 현황 확인
    total_clinics = Clinic.objects.count()
    total_reviews = Review.objects.count()
    total_sentiment = SentimentAnalysis.objects.count()
    total_price = PriceData.objects.count()
    
    logger.info(f"📊 삭제 전 데이터 현황:")
    logger.info(f"   - 치과: {total_clinics}개")
    logger.info(f"   - 리뷰: {total_reviews}개")
    logger.info(f"   - 감성분석: {total_sentiment}개")
    logger.info(f"   - 가격데이터: {total_price}개")
    logger.info("-" * 60)
    
    # 실제 크롤링 데이터 식별 (최근에 생성된 데이터들)
    # mass_naver, simple_naver, auto_naver로 시작하는 reviewer_hash를 가진 리뷰들은 보존
    real_reviews = Review.objects.filter(
        reviewer_hash__startswith='mass_naver'
    ) | Review.objects.filter(
        reviewer_hash__startswith='simple_naver'
    ) | Review.objects.filter(
        reviewer_hash__startswith='auto_naver'
    )
    
    real_clinic_ids = set(real_reviews.values_list('clinic_id', flat=True))
    real_clinics = Clinic.objects.filter(id__in=real_clinic_ids)
    
    logger.info(f"🔍 실제 크롤링 데이터 식별:")
    logger.info(f"   - 실제 치과: {real_clinics.count()}개")
    logger.info(f"   - 실제 리뷰: {real_reviews.count()}개")
    logger.info("-" * 60)
    
    # 더미 데이터 삭제
    logger.info("🗑️ 더미 데이터 삭제 중...")
    
    # 1. 더미 리뷰와 관련 데이터 삭제
    dummy_reviews = Review.objects.exclude(id__in=real_reviews.values_list('id', flat=True))
    dummy_review_count = dummy_reviews.count()
    
    # 더미 리뷰의 감성분석 데이터 삭제
    dummy_sentiment_count = SentimentAnalysis.objects.filter(
        review__in=dummy_reviews
    ).count()
    SentimentAnalysis.objects.filter(review__in=dummy_reviews).delete()
    
    # 더미 리뷰의 가격 데이터 삭제
    dummy_price_count = PriceData.objects.filter(
        review__in=dummy_reviews
    ).count()
    PriceData.objects.filter(review__in=dummy_reviews).delete()
    
    # 더미 리뷰 삭제
    dummy_reviews.delete()
    
    logger.info(f"✅ 더미 리뷰 삭제: {dummy_review_count}개")
    logger.info(f"✅ 더미 감성분석 삭제: {dummy_sentiment_count}개")
    logger.info(f"✅ 더미 가격데이터 삭제: {dummy_price_count}개")
    
    # 2. 더미 치과 삭제 (리뷰가 없는 치과들)
    dummy_clinics = Clinic.objects.exclude(id__in=real_clinic_ids)
    dummy_clinic_count = dummy_clinics.count()
    dummy_clinics.delete()
    
    logger.info(f"✅ 더미 치과 삭제: {dummy_clinic_count}개")
    
    # 3. 실제 치과들의 통계 업데이트
    logger.info("📊 실제 치과 통계 업데이트 중...")
    updated_count = 0
    
    for clinic in real_clinics:
        clinic_reviews = Review.objects.filter(clinic=clinic)
        clinic.total_reviews = clinic_reviews.count()
        
        if clinic.total_reviews > 0:
            avg_rating = clinic_reviews.aggregate(
                avg=django.db.models.Avg('original_rating')
            )['avg']
            clinic.average_rating = round(avg_rating, 2)
        else:
            clinic.average_rating = 0
        
        clinic.save()
        updated_count += 1
    
    logger.info(f"✅ 치과 통계 업데이트: {updated_count}개")
    
    # 최종 결과 확인
    logger.info("-" * 60)
    final_clinics = Clinic.objects.count()
    final_reviews = Review.objects.count()
    final_sentiment = SentimentAnalysis.objects.count()
    final_price = PriceData.objects.count()
    
    logger.info(f"📊 삭제 후 데이터 현황:")
    logger.info(f"   - 치과: {final_clinics}개")
    logger.info(f"   - 리뷰: {final_reviews}개")
    logger.info(f"   - 감성분석: {final_sentiment}개")
    logger.info(f"   - 가격데이터: {final_price}개")
    
    logger.info("=" * 60)
    logger.info("✅ 더미 데이터 삭제 완료!")
    logger.info("🎯 이제 실제 크롤링 데이터만 남았습니다.")
    logger.info("=" * 60)

if __name__ == '__main__':
    clean_dummy_data()