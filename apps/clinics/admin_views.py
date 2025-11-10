"""
관리자용 뷰 - 데이터 생성 및 관리
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from decimal import Decimal
import random
import json
from datetime import timedelta

from .models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData


@csrf_exempt
@require_http_methods(["POST"])
def create_massive_data(request):
    """대량 데이터 생성 API"""
    try:
        # 요청 파라미터 파싱
        data = json.loads(request.body) if request.body else {}
        clinic_count = data.get('clinic_count', 100)
        clear_existing = data.get('clear_existing', False)
        
        result = {
            'status': 'success',
            'message': '대량 데이터 생성 시작',
            'data': {}
        }
        
        # 마이그레이션 먼저 실행
        try:
            from django.core.management import call_command
            call_command('migrate', verbosity=0)
            result['message'] += ' (마이그레이션 완료)'
        except Exception as e:
            result['message'] += f' (마이그레이션 오류: {str(e)})'
        
        # 기존 데이터 삭제 (옵션)
        if clear_existing:
            try:
                PriceData.objects.all().delete()
                SentimentAnalysis.objects.all().delete()
                Review.objects.all().delete()
                Clinic.objects.all().delete()
                result['message'] += ' (기존 데이터 삭제됨)'
            except Exception as e:
                # 테이블이 없는 경우 무시
                result['message'] += f' (기존 데이터 삭제 시도: {str(e)})'
        
        # 실제 치과 데이터 생성
        real_clinics_created = create_real_clinics()
        
        # 추가 치과 데이터 생성
        additional_clinics_created = create_additional_clinics(clinic_count)
        
        # 리뷰 및 분석 데이터 생성
        reviews_created = create_reviews_and_analysis()
        
        # 결과 정리
        result['data'] = {
            'real_clinics': real_clinics_created,
            'additional_clinics': additional_clinics_created,
            'total_clinics': Clinic.objects.count(),
            'total_reviews': Review.objects.count(),
            'total_sentiment_analysis': SentimentAnalysis.objects.count(),
            'total_price_data': PriceData.objects.count()
        }
        
        result['message'] = '대량 데이터 생성 완료'
        
        return JsonResponse(result)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'데이터 생성 중 오류 발생: {str(e)}'
        }, status=500)


def create_real_clinics():
    """실제 치과 정보 생성"""
    real_clinics = [
        {
            'name': '서울대학교치과병원',
            'district': '종로구',
            'address': '서울특별시 종로구 대학로 101',
            'phone': '02-2072-2114',
            'specialties': '구강외과, 치주과, 보존과, 보철과, 교정과, 소아치과',
            'description': '국내 최고 수준의 치과 의료진과 최신 장비를 보유한 대학병원',
            'latitude': 37.5802,
            'longitude': 127.0017
        },
        {
            'name': '연세대학교치과대학병원',
            'district': '서대문구',
            'address': '서울특별시 서대문구 연세로 50-1',
            'phone': '02-2228-8900',
            'specialties': '구강외과, 치주과, 보존과, 보철과, 교정과, 구강내과',
            'description': '70년 전통의 치과대학병원으로 우수한 의료진과 연구진을 보유',
            'latitude': 37.5636,
            'longitude': 126.9348
        },
        {
            'name': '강남세브란스병원 치과',
            'district': '강남구',
            'address': '서울특별시 강남구 언주로 211',
            'phone': '02-2019-3300',
            'specialties': '구강외과, 치주과, 보존과, 보철과, 임플란트',
            'description': '강남 지역 대표 종합병원 치과로 첨단 의료 시설 완비',
            'latitude': 37.5194,
            'longitude': 127.0473
        },
        {
            'name': '삼성서울병원 치과',
            'district': '강남구',
            'address': '서울특별시 강남구 일원로 81',
            'phone': '02-3410-2114',
            'specialties': '구강외과, 치주과, 보존과, 보철과, 교정과',
            'description': '삼성의료원 소속 치과로 최신 의료 기술과 우수한 의료진 보유',
            'latitude': 37.4881,
            'longitude': 127.0857
        },
        {
            'name': '서울아산병원 치과',
            'district': '송파구',
            'address': '서울특별시 송파구 올림픽로43길 88',
            'phone': '02-3010-3114',
            'specialties': '구강외과, 치주과, 보존과, 보철과, 소아치과',
            'description': '아산의료원 소속으로 종합적인 치과 진료 서비스 제공',
            'latitude': 37.5262,
            'longitude': 127.1059
        }
    ]
    
    created_count = 0
    for clinic_data in real_clinics:
        clinic, created = Clinic.objects.get_or_create(
            name=clinic_data['name'],
            defaults={
                'address': clinic_data['address'],
                'district': clinic_data['district'],
                'latitude': Decimal(str(clinic_data['latitude'])),
                'longitude': Decimal(str(clinic_data['longitude'])),
                'phone': clinic_data['phone'],
                'specialties': clinic_data['specialties'],
                'description': clinic_data['description'],
                'has_parking': True,
                'night_service': False,
                'weekend_service': True,
                'is_verified': True
            }
        )
        if created:
            created_count += 1
    
    return created_count


def create_additional_clinics(count):
    """추가 치과 데이터 생성"""
    districts = [
        '강남구', '강동구', '강북구', '강서구', '관악구',
        '광진구', '구로구', '금천구', '노원구', '도봉구',
        '동대문구', '동작구', '마포구', '서대문구', '서초구',
        '성동구', '성북구', '송파구', '양천구', '영등포구',
        '용산구', '은평구', '종로구', '중구', '중랑구'
    ]
    
    clinic_names = [
        '미소치과', '행복치과', '건강치과', '밝은치과', '새로운치과',
        '든든치과', '믿음치과', '정성치과', '친절치과', '전문치과',
        '우수치과', '최고치과', '안전치과', '깨끗한치과', '편안한치과'
    ]
    
    treatments = [
        '스케일링', '임플란트', '교정', '미백', '신경치료', '발치',
        '충치치료', '크라운', '브릿지', '틀니', '사랑니', '잇몸치료'
    ]
    
    created_count = 0
    for i in range(count):
        district = random.choice(districts)
        name = f"{district} {random.choice(clinic_names)}"
        
        # 중복 방지
        counter = 1
        original_name = name
        while Clinic.objects.filter(name=name).exists():
            name = f"{original_name} {counter}호점"
            counter += 1
        
        lat_base = 37.5665 + random.uniform(-0.15, 0.15)
        lng_base = 126.9780 + random.uniform(-0.15, 0.15)
        
        selected_treatments = random.sample(treatments, random.randint(3, 6))
        
        Clinic.objects.create(
            name=name,
            address=f"서울특별시 {district} {random.randint(1, 999)}번길 {random.randint(1, 100)}",
            district=district,
            latitude=Decimal(str(round(lat_base, 6))),
            longitude=Decimal(str(round(lng_base, 6))),
            phone=f"02-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
            has_parking=random.choice([True, False]),
            night_service=random.choice([True, False]),
            weekend_service=random.choice([True, False]),
            specialties=', '.join(selected_treatments),
            description=f"{district}에 위치한 {name}입니다. {', '.join(selected_treatments[:3])} 전문 치과입니다.",
            business_hours="평일 09:00-18:00, 토요일 09:00-13:00",
            is_verified=random.choice([True, False])
        )
        created_count += 1
    
    return created_count


def create_reviews_and_analysis():
    """리뷰 및 감성분석 데이터 생성"""
    positive_reviews = [
        "의사선생님이 정말 친절하시고 설명도 자세히 해주셔서 좋았어요. 치료 과정을 하나하나 설명해주시니 안심이 되었습니다.",
        "스케일링 받았는데 전혀 아프지 않게 해주셨어요. 직원분들도 친절하고 시설도 깨끗해서 만족합니다.",
        "임플란트 상담받았는데 다른 곳보다 가격도 합리적이고 설명이 자세해서 신뢰가 갔어요. 과잉진료 없이 정직하게 상담해주셨습니다.",
        "교정 상담 받았는데 여러 방법을 제시해주시고 장단점을 솔직하게 말씀해주셔서 좋았습니다. 가격도 투명하게 안내해주셨어요.",
        "신경치료 받았는데 아프지 않게 잘해주셨어요. 마취도 잘해주시고 치료 후 주의사항도 자세히 설명해주셨습니다.",
        "충치치료 받았는데 꼼꼼하게 잘해주셨어요. 치료 후 관리 방법도 자세히 알려주시고 예약 시간도 잘 지켜주세요.",
        "미백 받았는데 효과가 정말 좋아요. 가격 대비 만족도가 높습니다. 시설도 깨끗하고 현대적이에요.",
        "발치 받았는데 생각보다 전혀 아프지 않았어요. 의사선생님 실력이 정말 좋으신 것 같아요.",
        "정기검진 받았는데 꼼꼼하게 봐주시고 예방 관리법도 알려주셔서 만족합니다. 다음에도 여기서 받을 예정이에요.",
        "크라운 치료받았는데 자연스럽게 잘 나왔어요. 색깔 맞춤도 완벽하고 씹는 느낌도 자연스러워요."
    ]
    
    negative_reviews = [
        "가격이 너무 비싸요. 다른 곳보다 훨씬 비싸면서 서비스는 별로였어요.",
        "대기시간이 너무 길어서 힘들었어요. 예약 시간보다 1시간 넘게 기다렸습니다.",
        "과잉진료 의심스러워요. 꼭 필요하지 않은 치료까지 권하시는 것 같아요.",
        "직원분들이 불친절해요. 설명도 대충하시고 성의가 없어 보였습니다.",
        "시설이 좀 오래된 것 같아요. 장비도 구식인 것 같고 청결도가 아쉬워요.",
        "치료 후 아픈데 제대로 처치해주지 않으셨어요. 다시 가기 싫습니다.",
        "예약이 어려워요. 전화해도 잘 안 받으시고 일정 조정이 힘들어요.",
        "주차가 불편해요. 주차공간이 부족해서 매번 고생합니다."
    ]
    
    clinics = Clinic.objects.all()
    total_reviews = 0
    
    for clinic in clinics:
        review_count = random.randint(15, 80)
        
        for _ in range(review_count):
            is_positive = random.random() < 0.7
            
            if is_positive:
                review_text = random.choice(positive_reviews)
                rating = random.choices([3, 4, 5], weights=[15, 35, 50])[0]
                base_scores = {
                    'price': random.uniform(0.1, 1.0),
                    'skill': random.uniform(0.2, 1.0),
                    'kindness': random.uniform(0.1, 1.0),
                    'waiting_time': random.uniform(0.0, 0.9),
                    'facility': random.uniform(0.1, 1.0),
                    'overtreatment': random.uniform(0.2, 1.0),
                }
            else:
                review_text = random.choice(negative_reviews)
                rating = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
                base_scores = {
                    'price': random.uniform(-1.0, 0.0),
                    'skill': random.uniform(-1.0, 0.2),
                    'kindness': random.uniform(-1.0, 0.0),
                    'waiting_time': random.uniform(-1.0, -0.1),
                    'facility': random.uniform(-1.0, 0.1),
                    'overtreatment': random.uniform(-1.0, -0.1),
                }
            
            review_date = timezone.now() - timedelta(days=random.randint(1, 730))
            
            review = Review.objects.create(
                clinic=clinic,
                source=random.choice(['naver', 'google', 'kakao']),
                original_text=review_text,
                processed_text=review_text,
                original_rating=rating,
                review_date=review_date,
                reviewer_hash=f"user_{random.randint(10000, 999999)}",
                external_id=f"{clinic.id}_{random.randint(100000, 999999)}",
                is_processed=True,
                is_duplicate=False
            )
            
            SentimentAnalysis.objects.create(
                review=review,
                price_score=Decimal(str(round(base_scores['price'], 2))),
                skill_score=Decimal(str(round(base_scores['skill'], 2))),
                kindness_score=Decimal(str(round(base_scores['kindness'], 2))),
                waiting_time_score=Decimal(str(round(base_scores['waiting_time'], 2))),
                facility_score=Decimal(str(round(base_scores['facility'], 2))),
                overtreatment_score=Decimal(str(round(base_scores['overtreatment'], 2))),
                model_version='api_v1.0',
                confidence_score=Decimal(str(round(random.uniform(0.70, 0.99), 2)))
            )
            
            total_reviews += 1
        
        # 치과 통계 업데이트
        reviews = Review.objects.filter(clinic=clinic)
        clinic.total_reviews = reviews.count()
        if reviews.exists():
            clinic.average_rating = Decimal(str(round(
                sum(r.original_rating for r in reviews) / reviews.count(), 2
            )))
        clinic.save()
    
    return total_reviews


@require_http_methods(["GET"])
def data_status(request):
    """현재 데이터 상태 확인"""
    return JsonResponse({
        'status': 'success',
        'data': {
            'clinics': Clinic.objects.count(),
            'reviews': Review.objects.count(),
            'sentiment_analysis': SentimentAnalysis.objects.count(),
            'price_data': PriceData.objects.count()
        }
    })


@csrf_exempt
@require_http_methods(["POST"])
def run_migrations(request):
    """데이터베이스 마이그레이션 실행"""
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # 마이그레이션 실행
        out = StringIO()
        call_command('migrate', stdout=out)
        
        return JsonResponse({
            'status': 'success',
            'message': '마이그레이션 완료',
            'output': out.getvalue()
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'마이그레이션 실행 중 오류: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def check_tables(request):
    """데이터베이스 테이블 존재 확인"""
    try:
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name LIKE '%clinic%' OR table_name LIKE '%review%' OR table_name LIKE '%analysis%'
                ORDER BY table_name;
            """)
            tables = [row[0] for row in cursor.fetchall()]
        
        return JsonResponse({
            'status': 'success',
            'tables': tables,
            'count': len(tables)
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'테이블 확인 중 오류: {str(e)}'
        }, status=500)