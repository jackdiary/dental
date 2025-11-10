#!/usr/bin/env python
"""
생성된 모든 데이터를 txt 파일로 내보내는 스크립트
"""
import os
import sys
import django
from datetime import datetime

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData

def export_clinics_data():
    """치과 데이터를 txt 파일로 내보내기"""
    print("🏥 치과 데이터 내보내는 중...")
    
    clinics = Clinic.objects.all().order_by('district', 'name')
    
    with open('massive_clinics_data.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("대량 치과 데이터 (총 {}개)\n".format(clinics.count()))
        f.write("생성일시: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        f.write("=" * 100 + "\n\n")
        
        current_district = None
        for i, clinic in enumerate(clinics, 1):
            if current_district != clinic.district:
                current_district = clinic.district
                f.write(f"\n📍 {current_district}\n")
                f.write("-" * 50 + "\n")
            
            f.write(f"{i:3d}. {clinic.name}\n")
            f.write(f"     주소: {clinic.address}\n")
            f.write(f"     전화: {clinic.phone}\n")
            f.write(f"     전문분야: {clinic.specialties}\n")
            f.write(f"     리뷰수: {clinic.total_reviews}개, 평점: {clinic.average_rating}\n")
            f.write(f"     주차: {'가능' if clinic.has_parking else '불가능'}, ")
            f.write(f"야간진료: {'가능' if clinic.night_service else '불가능'}, ")
            f.write(f"주말진료: {'가능' if clinic.weekend_service else '불가능'}\n")
            f.write(f"     설명: {clinic.description}\n")
            f.write(f"     좌표: ({clinic.latitude}, {clinic.longitude})\n")
            f.write("\n")
    
    print(f"✅ 치과 데이터 내보내기 완료: massive_clinics_data.txt ({clinics.count()}개)")

def export_reviews_data():
    """리뷰 데이터를 txt 파일로 내보내기"""
    print("📝 리뷰 데이터 내보내는 중...")
    
    reviews = Review.objects.select_related('clinic').all().order_by('clinic__name', '-review_date')
    
    with open('massive_reviews_data.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("대량 리뷰 데이터 (총 {}개)\n".format(reviews.count()))
        f.write("생성일시: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        f.write("=" * 100 + "\n\n")
        
        current_clinic = None
        clinic_review_count = 0
        
        for i, review in enumerate(reviews, 1):
            if current_clinic != review.clinic.name:
                if current_clinic:
                    f.write(f"   (총 {clinic_review_count}개 리뷰)\n\n")
                
                current_clinic = review.clinic.name
                clinic_review_count = 0
                f.write(f"🏥 {review.clinic.name} ({review.clinic.district})\n")
                f.write("-" * 80 + "\n")
            
            clinic_review_count += 1
            f.write(f"  [{clinic_review_count:3d}] ⭐{review.original_rating}점 | {review.source} | {review.review_date.strftime('%Y-%m-%d')}\n")
            f.write(f"       {review.original_text}\n")
            f.write(f"       리뷰어: {review.reviewer_hash} | ID: {review.external_id}\n\n")
        
        if current_clinic:
            f.write(f"   (총 {clinic_review_count}개 리뷰)\n\n")
    
    print(f"✅ 리뷰 데이터 내보내기 완료: massive_reviews_data.txt ({reviews.count()}개)")

def export_sentiment_analysis_data():
    """감성분석 데이터를 txt 파일로 내보내기"""
    print("🧠 감성분석 데이터 내보내는 중...")
    
    analyses = SentimentAnalysis.objects.select_related('review', 'review__clinic').all().order_by('review__clinic__name')
    
    with open('massive_sentiment_analysis_data.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("대량 감성분석 데이터 (총 {}개)\n".format(analyses.count()))
        f.write("생성일시: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        f.write("=" * 100 + "\n\n")
        
        f.write("감성분석 점수 범위: -1.0 (매우 부정) ~ +1.0 (매우 긍정)\n")
        f.write("분석 항목: 가격, 실력, 친절도, 대기시간, 시설, 과잉진료\n\n")
        
        current_clinic = None
        clinic_analysis_count = 0
        
        for i, analysis in enumerate(analyses, 1):
            if current_clinic != analysis.review.clinic.name:
                if current_clinic:
                    f.write(f"   (총 {clinic_analysis_count}개 분석)\n\n")
                
                current_clinic = analysis.review.clinic.name
                clinic_analysis_count = 0
                f.write(f"🏥 {analysis.review.clinic.name}\n")
                f.write("-" * 60 + "\n")
            
            clinic_analysis_count += 1
            f.write(f"  [{clinic_analysis_count:3d}] 리뷰 평점: {analysis.review.original_rating}점 | 신뢰도: {analysis.confidence_score}\n")
            f.write(f"       가격: {analysis.price_score:+.2f} | 실력: {analysis.skill_score:+.2f} | 친절도: {analysis.kindness_score:+.2f}\n")
            f.write(f"       대기시간: {analysis.waiting_time_score:+.2f} | 시설: {analysis.facility_score:+.2f} | 과잉진료: {analysis.overtreatment_score:+.2f}\n")
            f.write(f"       모델: {analysis.model_version}\n")
            f.write(f"       리뷰: {analysis.review.original_text[:100]}{'...' if len(analysis.review.original_text) > 100 else ''}\n\n")
        
        if current_clinic:
            f.write(f"   (총 {clinic_analysis_count}개 분석)\n\n")
    
    print(f"✅ 감성분석 데이터 내보내기 완료: massive_sentiment_analysis_data.txt ({analyses.count()}개)")

def export_price_data():
    """가격 데이터를 txt 파일로 내보내기"""
    print("💰 가격 데이터 내보내는 중...")
    
    prices = PriceData.objects.select_related('clinic', 'review').all().order_by('treatment_type', 'price')
    
    with open('massive_price_data.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("대량 가격 데이터 (총 {}개)\n".format(prices.count()))
        f.write("생성일시: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        f.write("=" * 100 + "\n\n")
        
        # 치료별 가격 통계
        from django.db.models import Count, Avg, Min, Max
        treatment_stats = prices.values('treatment_type').annotate(
            count=Count('id'),
            avg_price=Avg('price'),
            min_price=Min('price'),
            max_price=Max('price')
        ).order_by('-count')
        
        f.write("📊 치료별 가격 통계\n")
        f.write("-" * 80 + "\n")
        for stat in treatment_stats:
            f.write(f"{stat['treatment_type']:15s} | ")
            f.write(f"건수: {stat['count']:4d} | ")
            f.write(f"평균: {stat['avg_price']:8.0f}원 | ")
            f.write(f"최저: {stat['min_price']:8.0f}원 | ")
            f.write(f"최고: {stat['max_price']:8.0f}원\n")
        f.write("\n")
        
        # 상세 가격 데이터
        f.write("📋 상세 가격 데이터\n")
        f.write("-" * 80 + "\n")
        
        current_treatment = None
        treatment_count = 0
        
        for i, price in enumerate(prices, 1):
            if current_treatment != price.treatment_type:
                if current_treatment:
                    f.write(f"   (총 {treatment_count}건)\n\n")
                
                current_treatment = price.treatment_type
                treatment_count = 0
                f.write(f"🦷 {price.treatment_type}\n")
                f.write("-" * 50 + "\n")
            
            treatment_count += 1
            f.write(f"  [{treatment_count:3d}] {price.price:8.0f}원 | {price.clinic.name} ({price.clinic.district})\n")
            f.write(f"       신뢰도: {price.extraction_confidence} | 방법: {price.extraction_method}\n")
            f.write(f"       리뷰: {price.review.original_text[:80]}{'...' if len(price.review.original_text) > 80 else ''}\n\n")
        
        if current_treatment:
            f.write(f"   (총 {treatment_count}건)\n\n")
    
    print(f"✅ 가격 데이터 내보내기 완료: massive_price_data.txt ({prices.count()}개)")

def export_summary_statistics():
    """전체 통계 요약을 txt 파일로 내보내기"""
    print("📊 통계 요약 내보내는 중...")
    
    with open('massive_data_summary.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 100 + "\n")
        f.write("대량 치과 데이터 통계 요약\n")
        f.write("생성일시: {}\n".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        f.write("=" * 100 + "\n\n")
        
        # 전체 현황
        f.write("📈 전체 데이터 현황\n")
        f.write("-" * 50 + "\n")
        f.write(f"총 치과 수: {Clinic.objects.count():,}개\n")
        f.write(f"총 리뷰 수: {Review.objects.count():,}개\n")
        f.write(f"총 감성분석: {SentimentAnalysis.objects.count():,}개\n")
        f.write(f"총 가격데이터: {PriceData.objects.count():,}개\n\n")
        
        # 지역별 분포
        from django.db.models import Count, Avg
        f.write("📍 지역별 치과 분포\n")
        f.write("-" * 50 + "\n")
        districts = Clinic.objects.values('district').annotate(
            clinic_count=Count('id'),
            avg_reviews=Avg('total_reviews'),
            avg_rating=Avg('average_rating')
        ).order_by('-clinic_count')
        
        for district in districts:
            f.write(f"{district['district']:8s} | ")
            f.write(f"치과: {district['clinic_count']:3d}개 | ")
            f.write(f"평균 리뷰: {district['avg_reviews']:5.1f}개 | ")
            f.write(f"평균 평점: {district['avg_rating']:4.2f}점\n")
        f.write("\n")
        
        # 평점 분포
        f.write("⭐ 리뷰 평점 분포\n")
        f.write("-" * 50 + "\n")
        ratings = Review.objects.values('original_rating').annotate(count=Count('id')).order_by('original_rating')
        total_reviews = Review.objects.count()
        
        for rating in ratings:
            percentage = (rating['count'] / total_reviews) * 100
            f.write(f"{rating['original_rating']}점: {rating['count']:6,}개 ({percentage:5.1f}%)\n")
        f.write("\n")
        
        # 리뷰 소스 분포
        f.write("📱 리뷰 소스 분포\n")
        f.write("-" * 50 + "\n")
        sources = Review.objects.values('source').annotate(count=Count('id')).order_by('-count')
        for source in sources:
            percentage = (source['count'] / total_reviews) * 100
            f.write(f"{source['source']:10s}: {source['count']:6,}개 ({percentage:5.1f}%)\n")
        f.write("\n")
        
        # 치과 서비스 분포
        f.write("🏥 치과 서비스 분포\n")
        f.write("-" * 50 + "\n")
        total_clinics = Clinic.objects.count()
        parking_count = Clinic.objects.filter(has_parking=True).count()
        night_count = Clinic.objects.filter(night_service=True).count()
        weekend_count = Clinic.objects.filter(weekend_service=True).count()
        verified_count = Clinic.objects.filter(is_verified=True).count()
        
        f.write(f"주차 가능: {parking_count:3d}개 ({(parking_count/total_clinics)*100:5.1f}%)\n")
        f.write(f"야간 진료: {night_count:3d}개 ({(night_count/total_clinics)*100:5.1f}%)\n")
        f.write(f"주말 진료: {weekend_count:3d}개 ({(weekend_count/total_clinics)*100:5.1f}%)\n")
        f.write(f"인증 치과: {verified_count:3d}개 ({(verified_count/total_clinics)*100:5.1f}%)\n\n")
        
        # 상위 치과 (리뷰 수 기준)
        f.write("🏆 상위 20개 치과 (리뷰 수 기준)\n")
        f.write("-" * 80 + "\n")
        top_clinics = Clinic.objects.order_by('-total_reviews')[:20]
        for i, clinic in enumerate(top_clinics, 1):
            f.write(f"{i:2d}. {clinic.name:30s} | {clinic.district:8s} | ")
            f.write(f"{clinic.total_reviews:3d}개 리뷰 | {clinic.average_rating:4.2f}점\n")
        f.write("\n")
        
        # 최고 평점 치과
        f.write("⭐ 상위 20개 치과 (평점 기준, 리뷰 10개 이상)\n")
        f.write("-" * 80 + "\n")
        top_rated = Clinic.objects.filter(total_reviews__gte=10).order_by('-average_rating')[:20]
        for i, clinic in enumerate(top_rated, 1):
            f.write(f"{i:2d}. {clinic.name:30s} | {clinic.district:8s} | ")
            f.write(f"{clinic.average_rating:4.2f}점 | {clinic.total_reviews:3d}개 리뷰\n")
    
    print("✅ 통계 요약 내보내기 완료: massive_data_summary.txt")

def main():
    """모든 데이터 내보내기 실행"""
    print("🚀 대량 데이터를 txt 파일로 내보내기 시작...")
    print("=" * 80)
    
    # 1. 치과 데이터 내보내기
    export_clinics_data()
    
    # 2. 리뷰 데이터 내보내기
    export_reviews_data()
    
    # 3. 감성분석 데이터 내보내기
    export_sentiment_analysis_data()
    
    # 4. 가격 데이터 내보내기
    export_price_data()
    
    # 5. 통계 요약 내보내기
    export_summary_statistics()
    
    print("=" * 80)
    print("✅ 모든 데이터 내보내기 완료!")
    print("📁 생성된 파일:")
    print("   - massive_clinics_data.txt (치과 정보)")
    print("   - massive_reviews_data.txt (리뷰 데이터)")
    print("   - massive_sentiment_analysis_data.txt (감성분석)")
    print("   - massive_price_data.txt (가격 정보)")
    print("   - massive_data_summary.txt (통계 요약)")
    print("=" * 80)

if __name__ == '__main__':
    main()