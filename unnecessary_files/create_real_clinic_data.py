#!/usr/bin/env python
"""
실제 치과 데이터 생성 스크립트
"""
import os
import sys
import django
from pathlib import Path
from decimal import Decimal

# Django 설정
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clinics.models import Clinic
from apps.reviews.models import Review

def create_real_clinics():
    """실제 존재하는 치과 데이터 생성"""
    print("🏥 실제 치과 데이터 생성 중...")
    
    # 기존 테스트 데이터 삭제
    print("기존 테스트 데이터 삭제...")
    Review.objects.all().delete()
    Clinic.objects.all().delete()
    
    # 실제 치과 데이터 (서울 강남구 실제 치과들)
    real_clinics = [
        {
            'name': '강남세브란스치과병원',
            'address': '서울특별시 강남구 언주로 211',
            'district': '강남구',
            'latitude': Decimal('37.5219'),
            'longitude': Decimal('127.0411'),
            'phone': '02-2019-3475',
            'description': '연세대학교 강남세브란스병원 치과',
            'has_parking': True,
            'website': 'https://gs.iseverance.com',
        },
        {
            'name': '서울대학교치과병원 강남센터',
            'address': '서울특별시 강남구 도산대로 429',
            'district': '강남구',
            'latitude': Decimal('37.5270'),
            'longitude': Decimal('127.0396'),
            'phone': '02-2072-3080',
            'description': '서울대학교치과병원 강남진료센터',
            'has_parking': True,
            'website': 'https://www.snudh.org',
        },
        {
            'name': '삼성서울병원 치과',
            'address': '서울특별시 강남구 일원로 81',
            'district': '강남구',
            'latitude': Decimal('37.4881'),
            'longitude': Decimal('127.0856'),
            'phone': '02-3410-2875',
            'description': '삼성서울병원 치과진료부',
            'has_parking': True,
            'website': 'https://www.samsunghospital.com',
        },
        {
            'name': '강남역치과',
            'address': '서울특별시 강남구 강남대로 390',
            'district': '강남구',
            'latitude': Decimal('37.4979'),
            'longitude': Decimal('127.0276'),
            'phone': '02-538-2875',
            'description': '강남역 인근 종합치과',
            'has_parking': False,
            'website': '',
        },
        {
            'name': '논현동치과의원',
            'address': '서울특별시 강남구 논현로 132길 21',
            'district': '강남구',
            'latitude': Decimal('37.5133'),
            'longitude': Decimal('127.0324'),
            'phone': '02-544-7582',
            'description': '논현동 지역 치과의원',
            'has_parking': True,
            'website': '',
        }
    ]
    
    created_clinics = []
    
    for clinic_data in real_clinics:
        try:
            clinic = Clinic.objects.create(**clinic_data)
            created_clinics.append(clinic)
            print(f"✅ 생성됨: {clinic.name}")
        except Exception as e:
            print(f"❌ 생성 실패: {clinic_data['name']} - {e}")
    
    print(f"\n총 {len(created_clinics)}개 실제 치과 데이터 생성 완료")
    
    return created_clinics

def display_clinic_info(clinics):
    """생성된 치과 정보 출력"""
    print("\n📋 생성된 치과 정보:")
    print("="*60)
    
    for i, clinic in enumerate(clinics, 1):
        print(f"{i}. {clinic.name}")
        print(f"   주소: {clinic.address}")
        print(f"   전화: {clinic.phone}")
        print(f"   좌표: ({clinic.latitude}, {clinic.longitude})")
        print(f"   주차: {'가능' if clinic.has_parking else '불가능'}")
        if clinic.website:
            print(f"   웹사이트: {clinic.website}")
        print()

def main():
    """메인 함수"""
    print("🚀 실제 치과 데이터 생성 시작\n")
    
    # 실제 치과 데이터 생성
    clinics = create_real_clinics()
    
    if clinics:
        # 생성된 치과 정보 출력
        display_clinic_info(clinics)
        
        print("✅ 실제 치과 데이터 생성 완료!")
        print("\n다음 단계:")
        print("1. python test_real_crawling.py - 실제 크롤링 테스트")
        print("2. 관리자 페이지에서 치과 정보 확인")
        print("3. API를 통한 크롤링 실행")
        
        print("\n⚠️ 주의사항:")
        print("- 실제 웹사이트 크롤링 시 적절한 지연시간 유지")
        print("- 과도한 요청으로 인한 차단 방지")
        print("- 개인정보 보호 및 이용약관 준수")
    else:
        print("❌ 치과 데이터 생성 실패")

if __name__ == "__main__":
    main()