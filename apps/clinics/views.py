from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from django.db.models.functions import Coalesce
from .models import Clinic
from .serializers import (
    ClinicListSerializer, 
    ClinicDetailSerializer, 
    ClinicCreateSerializer,
    ClinicUpdateSerializer
)
from .location_services import location_service, LocationUtils


class ClinicPagination(PageNumberPagination):
    """치과 목록 페이지네이션"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ClinicListCreateView(generics.ListCreateAPIView):
    """치과 목록 조회 및 생성"""
    queryset = Clinic.objects.all()
    
    # 정렬에 사용할 기본 지표 주입 (NULL일 때 0으로 처리)
    queryset = queryset.annotate(
        avg_rating_filled=Coalesce('average_rating', 0.0),
        total_reviews_filled=Coalesce('total_reviews', 0)
    )
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = ClinicPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['district', 'is_verified']
    search_fields = ['name', 'address', 'specialties']
    ordering_fields = ['name', 'created_at', 'total_reviews']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ClinicCreateSerializer
        return ClinicListSerializer
    
    def get_queryset(self):
        queryset = Clinic.objects.select_related().prefetch_related('reviews')
        
        # 지역 필터링
        district = self.request.query_params.get('district')
        if district:
            queryset = queryset.filter(district__icontains=district)
        
        # 검증된 치과만 보기
        verified_only = self.request.query_params.get('verified_only')
        if verified_only and verified_only.lower() == 'true':
            queryset = queryset.filter(is_verified=True)
        
        # 리뷰 수 최소값 필터
        min_reviews = self.request.query_params.get('min_reviews')
        if min_reviews:
            try:
                min_reviews = int(min_reviews)
                queryset = queryset.filter(total_reviews__gte=min_reviews)
            except ValueError:
                pass
        
        return queryset
    
    def perform_create(self, serializer):
        """치과 생성 시 추가 로직"""
        clinic = serializer.save()
        # 검색 벡터 업데이트
        clinic.update_search_vector()


class ClinicDetailView(generics.RetrieveUpdateDestroyAPIView):
    """치과 상세 정보 조회, 수정, 삭제"""
    queryset = Clinic.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ClinicUpdateSerializer
        return ClinicDetailSerializer
    
    def get_queryset(self):
        return Clinic.objects.prefetch_related(
            'reviews'
        ).select_related()
    
    def perform_update(self, serializer):
        """치과 정보 수정 시 검색 벡터 업데이트"""
        clinic = serializer.save()
        clinic.update_search_vector()


@api_view(['GET'])
@permission_classes([AllowAny])
def clinic_search(request):
    """치과 검색 API"""
    query = request.GET.get('q', '').strip()
    district = request.GET.get('district', '').strip()
    treatment = request.GET.get('treatment', '').strip()
    sort = request.GET.get('sort', 'recommended').strip()
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 20))
    
    queryset = Clinic.objects.all()
    
    # 텍스트 검색
    if query:
        queryset = queryset.filter(
            Q(name__icontains=query) |
            Q(address__icontains=query) |
            Q(specialties__icontains=query) |
            Q(description__icontains=query)
        )
    
    # 지역 필터
    if district:
        queryset = queryset.filter(district__icontains=district)
    
    # 치료 종류 필터
    if treatment:
        # specialties 필드에서 검색
        queryset = queryset.filter(specialties__icontains=treatment)
    
    # 정렬
    if sort == 'recommended':
        queryset = queryset.order_by('-total_reviews_filled', '-avg_rating_filled')
    elif sort == 'rating':
        queryset = queryset.order_by('-avg_rating_filled', '-total_reviews_filled')
    elif sort == 'reviews':
        queryset = queryset.order_by('-total_reviews_filled', '-avg_rating_filled')
    elif sort == 'name':
        queryset = queryset.order_by('name')
    else:
        queryset = queryset.order_by('-total_reviews', '-average_rating')
    
    # 페이지네이션
    total_count = queryset.count()
    start = (page - 1) * page_size
    end = start + page_size
    queryset = queryset[start:end]
    
    serializer = ClinicListSerializer(queryset, many=True)
    
    # 페이지네이션 정보 계산
    has_next = end < total_count
    has_previous = page > 1
    
    return Response({
        'results': serializer.data,
        'count': total_count,
        'next': f"?page={page + 1}" if has_next else None,
        'previous': f"?page={page - 1}" if has_previous else None,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size,
        'query': query,
        'district': district,
        'treatment': treatment,
        'sort': sort
    })

@api_view(['GET'])
@permission_classes([AllowAny])
def clinic_nearby(request):
    """근처 치과 검색 API"""
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    radius = float(request.GET.get('radius', 5.0))  # 기본 5km
    
    if not lat or not lng:
        return Response({
            'error': '위도(lat)와 경도(lng) 파라미터가 필요합니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        lat = float(lat)
        lng = float(lng)
    except ValueError:
        return Response({
            'error': '올바른 위도와 경도 값을 입력해주세요.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # 근처 치과 검색 (간단한 거리 계산)
    queryset = Clinic.objects.all()
    nearby_clinics = []
    
    for clinic in queryset:
        if clinic.latitude and clinic.longitude:
            distance = LocationUtils.calculate_distance(
                lat, lng, clinic.latitude, clinic.longitude
            )
            if distance <= radius:
                clinic_data = ClinicListSerializer(clinic).data
                clinic_data['distance'] = round(distance, 2)
                nearby_clinics.append(clinic_data)
    
    # 거리순 정렬
    nearby_clinics.sort(key=lambda x: x['distance'])
    
    return Response({
        'results': nearby_clinics,
        'count': len(nearby_clinics),
        'center': {'lat': lat, 'lng': lng},
        'radius': radius
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def clinic_by_district_and_location(request):
    """지역별 치과 목록 API"""
    district = request.GET.get('district', '').strip()
    location = request.GET.get('location', '').strip()
    
    queryset = Clinic.objects.all()
    
    if district:
        queryset = queryset.filter(district__icontains=district)
    
    if location:
        queryset = queryset.filter(
            Q(address__icontains=location) |
            Q(district__icontains=location)
        )
    
    queryset = queryset.order_by('-total_reviews', '-average_rating')
    
    serializer = ClinicListSerializer(queryset, many=True)
    
    return Response({
        'results': serializer.data,
        'count': queryset.count(),
        'district': district,
        'location': location
    })


@api_view(['POST'])
@permission_classes([AllowAny])
def geocode_address(request):
    """주소를 좌표로 변환"""
    address = request.data.get('address', '').strip()
    
    if not address:
        return Response({
            'error': '주소가 필요합니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        coordinates = location_service.geocode_address(address)
        if coordinates:
            return Response({
                'address': address,
                'latitude': coordinates[0],
                'longitude': coordinates[1]
            })
        else:
            return Response({
                'error': '주소를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'지오코딩 오류: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def reverse_geocode(request):
    """좌표를 주소로 변환"""
    lat = request.data.get('lat')
    lng = request.data.get('lng')
    
    if not lat or not lng:
        return Response({
            'error': '위도(lat)와 경도(lng)가 필요합니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        lat = float(lat)
        lng = float(lng)
        
        address = location_service.reverse_geocode(lat, lng)
        if address:
            return Response({
                'latitude': lat,
                'longitude': lng,
                'address': address
            })
        else:
            return Response({
                'error': '주소를 찾을 수 없습니다.'
            }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'error': f'역지오코딩 오류: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def nearby_districts(request):
    """근처 지역구 목록"""
    lat = request.GET.get('lat')
    lng = request.GET.get('lng')
    
    if not lat or not lng:
        return Response({
            'error': '위도(lat)와 경도(lng) 파라미터가 필요합니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        lat = float(lat)
        lng = float(lng)
        
        # 서울 지역구 목록 (간단한 예시)
        seoul_districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구',
            '광진구', '구로구', '금천구', '노원구', '도봉구',
            '동대문구', '동작구', '마포구', '서대문구', '서초구',
            '성동구', '성북구', '송파구', '양천구', '영등포구',
            '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
        
        return Response({
            'districts': seoul_districts,
            'center': {'lat': lat, 'lng': lng}
        })
        
    except ValueError:
        return Response({
            'error': '올바른 위도와 경도 값을 입력해주세요.'
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def seoul_districts(request):
    """서울 지역구 목록"""
    districts = [
        '강남구', '강동구', '강북구', '강서구', '관악구',
        '광진구', '구로구', '금천구', '노원구', '도봉구',
        '동대문구', '동작구', '마포구', '서대문구', '서초구',
        '성동구', '성북구', '송파구', '양천구', '영등포구',
        '용산구', '은평구', '종로구', '중구', '중랑구'
    ]
    
    return Response({
        'districts': districts,
        'count': len(districts)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def clinic_districts(request):
    """치과가 있는 지역구 목록"""
    districts = Clinic.objects.values_list('district', flat=True).distinct().order_by('district')
    districts = [d for d in districts if d]  # 빈 값 제거
    
    return Response({
        'districts': list(districts),
        'count': len(districts)
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def clinic_stats(request):
    """치과 통계 정보"""
    total_clinics = Clinic.objects.count()
    verified_clinics = Clinic.objects.filter(is_verified=True).count()
    
    # 지역별 통계
    district_stats = Clinic.objects.values('district').annotate(
        count=Count('id'),
        avg_rating=Avg('average_rating')
    ).order_by('-count')[:10]
    
    # 평점 분포
    rating_stats = {
        '5점': Clinic.objects.filter(average_rating__gte=4.5).count(),
        '4점대': Clinic.objects.filter(average_rating__gte=4.0, average_rating__lt=4.5).count(),
        '3점대': Clinic.objects.filter(average_rating__gte=3.0, average_rating__lt=4.0).count(),
        '3점 미만': Clinic.objects.filter(average_rating__lt=3.0).count(),
    }
    
    return Response({
        'total_clinics': total_clinics,
        'verified_clinics': verified_clinics,
        'verification_rate': round(verified_clinics / total_clinics * 100, 1) if total_clinics > 0 else 0,
        'district_stats': list(district_stats),
        'rating_distribution': rating_stats
    })
