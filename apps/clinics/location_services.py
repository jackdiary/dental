"""
위치 기반 서비스 모듈
"""
from typing import List, Tuple, Optional, Dict
from decimal import Decimal
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
from django.db.models import Q
import logging

from .models import Clinic

logger = logging.getLogger(__name__)


class LocationService:
    """위치 기반 서비스"""
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent="dental-ai-system")
    
    def get_clinics_by_radius(
        self, 
        center_lat: float, 
        center_lng: float, 
        radius_km: float = 5.0,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        반경 내 치과 검색
        
        Args:
            center_lat: 중심점 위도
            center_lng: 중심점 경도
            radius_km: 검색 반경 (km)
            limit: 최대 결과 수
            
        Returns:
            거리 정보가 포함된 치과 목록
        """
        center_point = (center_lat, center_lng)
        
        # 모든 치과 조회 (위치 정보가 있는 것만)
        clinics = Clinic.objects.filter(
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        clinics_with_distance = []
        
        for clinic in clinics:
            clinic_point = (float(clinic.latitude), float(clinic.longitude))
            distance = geodesic(center_point, clinic_point).kilometers
            
            if distance <= radius_km:
                clinics_with_distance.append({
                    'clinic': clinic,
                    'distance_km': round(distance, 2),
                    'distance_m': round(distance * 1000),
                })
        
        # 거리순 정렬
        clinics_with_distance.sort(key=lambda x: x['distance_km'])
        
        # 제한 적용
        if limit:
            clinics_with_distance = clinics_with_distance[:limit]
        
        logger.info(f"반경 {radius_km}km 내 {len(clinics_with_distance)}개 치과 발견")
        
        return clinics_with_distance
    
    def get_clinics_by_district_and_radius(
        self,
        district: str,
        center_lat: Optional[float] = None,
        center_lng: Optional[float] = None,
        radius_km: float = 10.0,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        지역구 + 반경 조합 검색
        
        Args:
            district: 지역구명
            center_lat: 중심점 위도 (선택)
            center_lng: 중심점 경도 (선택)
            radius_km: 검색 반경
            limit: 최대 결과 수
            
        Returns:
            치과 목록 (거리 정보 포함)
        """
        # 기본적으로 지역구로 필터링
        clinics = Clinic.objects.filter(
            district__icontains=district,
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        clinics_with_distance = []
        
        # 사용자 위치가 제공된 경우 거리 계산
        if center_lat and center_lng:
            center_point = (center_lat, center_lng)
            
            for clinic in clinics:
                clinic_point = (float(clinic.latitude), float(clinic.longitude))
                distance = geodesic(center_point, clinic_point).kilometers
                
                if distance <= radius_km:
                    clinics_with_distance.append({
                        'clinic': clinic,
                        'distance_km': round(distance, 2),
                        'distance_m': round(distance * 1000),
                    })
            
            # 거리순 정렬
            clinics_with_distance.sort(key=lambda x: x['distance_km'])
        else:
            # 위치 정보가 없으면 거리 없이 반환
            for clinic in clinics:
                clinics_with_distance.append({
                    'clinic': clinic,
                    'distance_km': None,
                    'distance_m': None,
                })
        
        # 제한 적용
        if limit:
            clinics_with_distance = clinics_with_distance[:limit]
        
        return clinics_with_distance
    
    def geocode_address(self, address: str) -> Optional[Tuple[float, float]]:
        """
        주소를 좌표로 변환
        
        Args:
            address: 주소 문자열
            
        Returns:
            (위도, 경도) 튜플 또는 None
        """
        try:
            location = self.geocoder.geocode(address, timeout=10)
            if location:
                return (location.latitude, location.longitude)
        except Exception as e:
            logger.error(f"주소 지오코딩 실패: {address} - {e}")
        
        return None
    
    def reverse_geocode(self, lat: float, lng: float) -> Optional[str]:
        """
        좌표를 주소로 변환
        
        Args:
            lat: 위도
            lng: 경도
            
        Returns:
            주소 문자열 또는 None
        """
        try:
            location = self.geocoder.reverse((lat, lng), timeout=10)
            if location:
                return location.address
        except Exception as e:
            logger.error(f"좌표 역지오코딩 실패: ({lat}, {lng}) - {e}")
        
        return None
    
    def get_district_from_coordinates(self, lat: float, lng: float) -> Optional[str]:
        """
        좌표에서 지역구 추출
        
        Args:
            lat: 위도
            lng: 경도
            
        Returns:
            지역구명 또는 None
        """
        address = self.reverse_geocode(lat, lng)
        if address:
            # 한국 주소에서 구 단위 추출
            parts = address.split(',')
            for part in parts:
                part = part.strip()
                if '구' in part and ('시' not in part or part.endswith('구')):
                    # "강남구", "서초구" 등 추출
                    if part.endswith('구'):
                        return part
        
        return None
    
    def calculate_distance(
        self, 
        lat1: float, lng1: float, 
        lat2: float, lng2: float
    ) -> float:
        """
        두 지점 간 거리 계산
        
        Args:
            lat1, lng1: 첫 번째 지점 좌표
            lat2, lng2: 두 번째 지점 좌표
            
        Returns:
            거리 (km)
        """
        point1 = (lat1, lng1)
        point2 = (lat2, lng2)
        return geodesic(point1, point2).kilometers
    
    def get_nearby_districts(self, district: str, radius_km: float = 20.0) -> List[str]:
        """
        인근 지역구 찾기
        
        Args:
            district: 기준 지역구
            radius_km: 검색 반경
            
        Returns:
            인근 지역구 목록
        """
        # 기준 지역구의 치과들로부터 대표 좌표 계산
        base_clinics = Clinic.objects.filter(
            district__icontains=district,
            latitude__isnull=False,
            longitude__isnull=False
        )
        
        if not base_clinics.exists():
            return [district]
        
        # 평균 좌표 계산
        total_lat = sum(float(c.latitude) for c in base_clinics)
        total_lng = sum(float(c.longitude) for c in base_clinics)
        avg_lat = total_lat / len(base_clinics)
        avg_lng = total_lng / len(base_clinics)
        
        # 모든 지역구의 치과들 확인
        all_districts = Clinic.objects.values_list('district', flat=True).distinct()
        nearby_districts = [district]  # 기준 지역구 포함
        
        for other_district in all_districts:
            if other_district == district:
                continue
                
            other_clinics = Clinic.objects.filter(
                district=other_district,
                latitude__isnull=False,
                longitude__isnull=False
            ).first()
            
            if other_clinics:
                distance = self.calculate_distance(
                    avg_lat, avg_lng,
                    float(other_clinics.latitude), float(other_clinics.longitude)
                )
                
                if distance <= radius_km:
                    nearby_districts.append(other_district)
        
        return nearby_districts


class LocationUtils:
    """위치 관련 유틸리티 함수들"""
    
    @staticmethod
    def is_valid_coordinates(lat: float, lng: float) -> bool:
        """좌표 유효성 검사"""
        return (
            -90 <= lat <= 90 and 
            -180 <= lng <= 180 and
            not (lat == 0 and lng == 0)
        )
    
    @staticmethod
    def format_distance(distance_km: float) -> str:
        """거리를 사용자 친화적 형태로 포맷"""
        if distance_km < 1:
            return f"{int(distance_km * 1000)}m"
        elif distance_km < 10:
            return f"{distance_km:.1f}km"
        else:
            return f"{int(distance_km)}km"
    
    @staticmethod
    def get_seoul_districts() -> List[str]:
        """서울시 자치구 목록"""
        return [
            '강남구', '강동구', '강북구', '강서구', '관악구',
            '광진구', '구로구', '금천구', '노원구', '도봉구',
            '동대문구', '동작구', '마포구', '서대문구', '서초구',
            '성동구', '성북구', '송파구', '양천구', '영등포구',
            '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
    
    @staticmethod
    def get_district_center_coordinates() -> Dict[str, Tuple[float, float]]:
        """주요 지역구 중심 좌표"""
        return {
            '강남구': (37.5173, 127.0473),
            '서초구': (37.4837, 127.0324),
            '송파구': (37.5145, 127.1059),
            '강서구': (37.5509, 126.8495),
            '마포구': (37.5663, 126.9019),
            '종로구': (37.5735, 126.9788),
            '중구': (37.5641, 126.9979),
            '용산구': (37.5384, 126.9654),
        }


# 전역 서비스 인스턴스
location_service = LocationService()