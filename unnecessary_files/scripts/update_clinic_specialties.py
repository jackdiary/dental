#!/usr/bin/env python
"""
치과 전문분야(specialties) 정보 업데이트 스크립트
"""
import os
import sys
import django
import random

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clinics.models import Clinic

def update_clinic_specialties():
    """치과별로 전문분야 정보 추가"""
    
    # 치료 종류 목록
    treatments = [
        '스케일링', '임플란트', '교정', '미백', '신경치료', '발치',
        '충치치료', '크라운', '브릿지', '틀니', '사랑니', '잇몸치료',
        '치주치료', '보철치료', '소아치과', '구강외과'
    ]
    
    clinics = Clinic.objects.all()
    
    print(f"🦷 {clinics.count()}개 치과의 전문분야 정보 업데이트 중...")
    
    for clinic in clinics:
        # 각 치과마다 3-8개의 전문분야를 랜덤하게 선택
        num_specialties = random.randint(3, 8)
        selected_treatments = random.sample(treatments, num_specialties)
        
        # 쉼표로 구분된 문자열로 저장
        clinic.specialties = ', '.join(selected_treatments)
        clinic.save(update_fields=['specialties'])
    
    print(f"✅ {clinics.count()}개 치과 전문분야 정보 업데이트 완료!")
    
    # 샘플 출력
    sample_clinics = clinics[:3]
    print("\n📋 샘플 치과 전문분야:")
    for clinic in sample_clinics:
        print(f"  - {clinic.name}: {clinic.specialties}")

if __name__ == '__main__':
    update_clinic_specialties()