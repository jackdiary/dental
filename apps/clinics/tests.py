from django.test import TestCase
from django.db import IntegrityError
from decimal import Decimal
from .models import Clinic


class ClinicModelTest(TestCase):
    """치과 모델 테스트"""
    
    def setUp(self):
        self.clinic_data = {
            'name': '테스트 치과',
            'address': '서울특별시 강남구 테스트로 123',
            'district': '강남구',
            'latitude': Decimal('37.5172'),
            'longitude': Decimal('127.0473'),
            'phone': '02-1234-5678',
            'has_parking': True,
            'night_service': False,
            'weekend_service': True
        }
    
    def test_create_clinic(self):
        """치과 생성 테스트"""
        clinic = Clinic.objects.create(**self.clinic_data)
        
        self.assertEqual(clinic.name, '테스트 치과')
        self.assertEqual(clinic.district, '강남구')
        self.assertTrue(clinic.has_parking)
        self.assertFalse(clinic.night_service)
        self.assertEqual(clinic.total_reviews, 0)
        self.assertIsNone(clinic.average_rating)
    
    def test_clinic_string_representation(self):
        """치과 문자열 표현 테스트"""
        clinic = Clinic.objects.create(**self.clinic_data)
        expected_str = f"{clinic.name} ({clinic.district})"
        self.assertEqual(str(clinic), expected_str)
    
    def test_clinic_coordinates_validation(self):
        """치과 좌표 유효성 테스트"""
        clinic = Clinic.objects.create(**self.clinic_data)
        
        # 한국 범위 내 좌표 확인
        self.assertTrue(33.0 <= float(clinic.latitude) <= 39.0)
        self.assertTrue(124.0 <= float(clinic.longitude) <= 132.0)
    
    def test_update_search_vector(self):
        """검색 벡터 업데이트 테스트"""
        clinic = Clinic.objects.create(**self.clinic_data)
        
        # 검색 벡터가 자동으로 생성되는지 확인
        self.assertIsNotNone(clinic.search_vector)
    
    def test_update_review_stats(self):
        """리뷰 통계 업데이트 테스트"""
        clinic = Clinic.objects.create(**self.clinic_data)
        
        # 초기 상태 확인
        self.assertEqual(clinic.total_reviews, 0)
        self.assertIsNone(clinic.average_rating)
        
        # 리뷰 통계 업데이트 (실제 리뷰 없이 테스트)
        clinic.update_review_stats()
        self.assertEqual(clinic.total_reviews, 0)


class ClinicQueryTest(TestCase):
    """치과 쿼리 테스트"""
    
    def setUp(self):
        # 테스트용 치과들 생성
        self.clinic1 = Clinic.objects.create(
            name='강남 치과',
            address='서울특별시 강남구 강남대로 123',
            district='강남구',
            has_parking=True,
            night_service=True
        )
        
        self.clinic2 = Clinic.objects.create(
            name='서초 치과',
            address='서울특별시 서초구 서초대로 456',
            district='서초구',
            has_parking=False,
            weekend_service=True
        )
    
    def test_filter_by_district(self):
        """지역별 필터링 테스트"""
        gangnam_clinics = Clinic.objects.filter(district='강남구')
        self.assertEqual(gangnam_clinics.count(), 1)
        self.assertEqual(gangnam_clinics.first().name, '강남 치과')
    
    def test_filter_by_services(self):
        """서비스별 필터링 테스트"""
        parking_clinics = Clinic.objects.filter(has_parking=True)
        self.assertEqual(parking_clinics.count(), 1)
        
        night_clinics = Clinic.objects.filter(night_service=True)
        self.assertEqual(night_clinics.count(), 1)
        
        weekend_clinics = Clinic.objects.filter(weekend_service=True)
        self.assertEqual(weekend_clinics.count(), 1)
    
    def test_search_by_name(self):
        """이름으로 검색 테스트"""
        results = Clinic.objects.filter(name__icontains='강남')
        self.assertEqual(results.count(), 1)
        self.assertEqual(results.first().name, '강남 치과')