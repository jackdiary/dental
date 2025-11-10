#!/usr/bin/env python
"""
가격 데이터 생성 스크립트
기존 치과 데이터를 기반으로 가격 정보를 생성합니다.
"""
import os
import sys
import django
import random

# Django 설정
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.clinics.models import Clinic
from apps.analysis.models import PriceData

# 치료별 가격 범위 (원)
PRICE_RANGES = {
    'scaling': (50000, 150000),
    'implant': (1000000, 3000000),
    'root_canal': (100000, 500000),
    'orthodontics': (3000000, 8000000),
    'whitening': (200000, 800000),
    'extraction': (50000, 200000),
    'filling': (50000, 300000),
    'crown': (300000, 1000000),
    'bridge': (500000, 2000000),
    'denture': (800000, 3000000),
}

def create_price_data():
    """치과별로 가격 데이터 생성"""
    
    clinics = Clinic.objects.all()
    total_clinics = clinics.count()
    
    if total_clinics == 0:
        print("❌ 치과 데이터가 없습니다!")
        return
    
    print(f"📊 {total_clinics}개 치과에 대한 가격 데이터 생성 중...")
    
    created_count = 0
    
    for clinic in clinics:
        # 각 치과마다 3-5개의 치료 항목에 대한 가격 생성
        num_treatments = random.randint(3, 5)
        treatments = random.sample(list(PRICE_RANGES.keys()), num_treatments)
        
        for treatment_type in treatments:
            min_price, max_price = PRICE_RANGES[treatment_type]
            
            # 가격 생성 (범위 내에서 랜덤)
            base_price = random.randint(min_price, max_price)
            # 만원 단위로 반올림
            price = round(base_price / 10000) * 10000
            
            # 가격 데이터 생성
            PriceData.objects.create(
                clinic=clinic,
                treatment_type=treatment_type,
                price=price,
                currency='KRW',
                extraction_confidence=0.95,
                extraction_method='manual',
                is_verified=True,
                is_outlier=False
            )
            created_count += 1
    
    print(f"✅ {created_count}개의 가격 데이터 생성 완료!")
    
    # 통계 출력
    print("\n📈 치료 종류별 데이터 수:")
    for treatment_type in PRICE_RANGES.keys():
        count = PriceData.objects.filter(treatment_type=treatment_type).count()
        print(f"  - {treatment_type}: {count}개")

if __name__ == '__main__':
    # 기존 가격 데이터 삭제 여부 확인
    existing_count = PriceData.objects.count()
    if existing_count > 0:
        print(f"⚠️  기존 가격 데이터 {existing_count}개가 있습니다.")
        print("기존 데이터를 삭제하고 새로 생성합니다...")
        PriceData.objects.all().delete()
    
    create_price_data()
