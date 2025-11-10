"""
가격 비교 API 뷰
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Min, Max, Count
from apps.analysis.models import PriceData, RegionalPriceStats
from apps.clinics.models import Clinic


@api_view(['GET'])
def price_comparison(request):
    """
    지역별, 치료별 가격 비교 API
    """
    district = request.GET.get('district')
    treatment_type = request.GET.get('treatment_type')
    
    if not district or not treatment_type:
        return Response({
            'error': '지역(district)과 치료 종류(treatment_type)를 모두 제공해야 합니다.'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # 해당 지역, 치료의 가격 데이터 조회
        price_data = PriceData.objects.filter(
            clinic__district__icontains=district,
            treatment_type=treatment_type,
            is_verified=True,
            is_outlier=False
        ).select_related('clinic').order_by('price')
        
        if not price_data.exists():
            return Response({
                'prices': [],
                'stats': None,
                'message': '해당 조건의 가격 데이터가 없습니다.'
            })
        
        # 가격 통계 계산
        stats = price_data.aggregate(
            min_price=Min('price'),
            max_price=Max('price'),
            avg_price=Avg('price'),
            sample_count=Count('id')
        )
        
        # 치과별 가격 정보
        prices = []
        for price_item in price_data:
            clinic = price_item.clinic
            prices.append({
                'clinic_id': clinic.id,
                'clinic_name': clinic.name,
                'price': price_item.price,
                'address': clinic.address,
                'phone': clinic.phone,
                'has_parking': clinic.has_parking,
                'night_service': clinic.night_service,
                'weekend_service': clinic.weekend_service,
                'average_rating': float(clinic.average_rating) if clinic.average_rating else None,
                'total_reviews': clinic.total_reviews
            })
        
        return Response({
            'prices': prices,
            'stats': {
                'min_price': stats['min_price'],
                'max_price': stats['max_price'],
                'avg_price': float(stats['avg_price']),
                'sample_count': stats['sample_count']
            }
        })
        
    except Exception as e:
        return Response({
            'error': f'가격 비교 데이터 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def regional_price_stats(request):
    """
    지역별 가격 통계 API
    """
    district = request.GET.get('district')
    treatment_type = request.GET.get('treatment_type')
    
    try:
        queryset = RegionalPriceStats.objects.all()
        
        if district:
            queryset = queryset.filter(district__icontains=district)
        
        if treatment_type:
            queryset = queryset.filter(treatment_type=treatment_type)
        
        stats = []
        for stat in queryset:
            stats.append({
                'district': stat.district,
                'treatment_type': stat.treatment_type,
                'min_price': stat.min_price,
                'max_price': stat.max_price,
                'avg_price': float(stat.avg_price),
                'median_price': stat.median_price,
                'sample_count': stat.sample_count,
                'last_updated': stat.last_updated.isoformat()
            })
        
        return Response({
            'stats': stats,
            'count': len(stats)
        })
        
    except Exception as e:
        return Response({
            'error': f'지역별 가격 통계 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def treatment_types(request):
    """
    치료 종류 목록 API
    """
    try:
        # 실제 데이터에서 치료 종류 추출
        treatment_types = PriceData.objects.values_list(
            'treatment_type', flat=True
        ).distinct().order_by('treatment_type')
        
        # 치료 종류별 한국어 라벨
        treatment_labels = {
            'scaling': '스케일링',
            'implant': '임플란트',
            'root_canal': '신경치료',
            'orthodontics': '교정',
            'whitening': '미백',
            'extraction': '발치',
            'filling': '충치치료',
            'crown': '크라운',
            'bridge': '브릿지',
            'denture': '틀니',
            'other': '기타'
        }
        
        treatments = []
        for treatment_type in treatment_types:
            treatments.append({
                'value': treatment_type,
                'label': treatment_labels.get(treatment_type, treatment_type),
                'count': PriceData.objects.filter(
                    treatment_type=treatment_type,
                    is_verified=True
                ).count()
            })
        
        return Response({
            'treatments': treatments
        })
        
    except Exception as e:
        return Response({
            'error': f'치료 종류 목록 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)