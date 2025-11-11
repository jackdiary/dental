#!/usr/bin/env python
"""
가격 데이터 검증 상태 업데이트 스크립트
"""
import os
import sys
import django

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.analysis.models import PriceData

def update_price_verification():
    """모든 가격 데이터를 검증된 상태로 업데이트"""
    
    print("💰 가격 데이터 검증 상태 업데이트 중...")
    
    # 모든 PriceData를 검증된 상태로 업데이트
    updated_count = PriceData.objects.update(is_verified=True)
    
    print(f"✅ {updated_count}개 가격 데이터 검증 완료!")
    
    # 치료별 통계 출력
    print("\n📊 치료별 가격 데이터 통계:")
    treatment_stats = PriceData.objects.values('treatment_type').annotate(
        count=models.Count('id')
    ).order_by('-count')
    
    for stat in treatment_stats:
        print(f"   - {stat['treatment_type']}: {stat['count']}개")

if __name__ == '__main__':
    from django.db import models
    update_price_verification()