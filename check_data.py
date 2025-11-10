#!/usr/bin/env python
"""
생성된 데이터 확인 스크립트
"""
import os
import sys
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData
from django.db.models import Count, Avg

def main():
    print('=== 전체 데이터 현황 ===')
    print(f'총 치과 수: {Clinic.objects.count()}개')
    print(f'총 리뷰 수: {Review.objects.count()}개')
    print(f'총 감성분석 수: {SentimentAnalysis.objects.count()}개')
    print(f'총 가격데이터 수: {PriceData.objects.count()}개')
    print()

    print('=== 지역별 치과 분포 ===')
    districts = Clinic.objects.values('district').annotate(count=Count('id')).order_by('-count')
    for district in districts:
        print(f'{district["district"]}: {district["count"]}개')
    print()

    print('=== 평점 분포 ===')
    ratings = Review.objects.values('original_rating').annotate(count=Count('id')).order_by('original_rating')
    for rating in ratings:
        print(f'{rating["original_rating"]}점: {rating["count"]}개')
    print()

    print('=== 치료 종류별 가격 데이터 ===')
    treatments = PriceData.objects.values('treatment_type').annotate(count=Count('id')).order_by('-count')
    for treatment in treatments:
        print(f'{treatment["treatment_type"]}: {treatment["count"]}개')
    print()

    print('=== 상위 10개 치과 (리뷰 수 기준) ===')
    top_clinics = Clinic.objects.order_by('-total_reviews')[:10]
    for clinic in top_clinics:
        print(f'{clinic.name} ({clinic.district}): {clinic.total_reviews}개 리뷰, 평점 {clinic.average_rating}')

if __name__ == '__main__':
    main()