#!/usr/bin/env python
"""
실제 크롤링 테스트
"""
import os
import sys
import django

# Django 설정
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clinics.models import Clinic
from scripts.crawl_real_data import RealDataCrawler

def test_single_clinic_crawling():
    """단일 치과 크롤링 테스트"""
    print("🧪 단일 치과 크롤링 테스트")
    
    # 강남구 치과 하나 선택
    clinic = Clinic.objects.filter(district='강남구').first()
    
    if not clinic:
        print("❌ 강남구 치과를 찾을 수 없습니다.")
        return
    
    print(f"🏥 테스트 대상: {clinic.name} (ID: {clinic.id})")
    
    # 크롤러 생성 및 실행
    crawler = RealDataCrawler()
    
    try:
        # 최대 10개 리뷰만 테스트
        crawler.crawl_clinic_reviews(clinic.id, max_reviews=10)
        print("✅ 테스트 완료!")
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_single_clinic_crawling()