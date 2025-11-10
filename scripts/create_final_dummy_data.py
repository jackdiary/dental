#!/usr/bin/env python
"""
최종 더미 데이터 생성 스크립트
- 다양한 가격 정보
- 차별화된 편의시설
- 위치 기반 검색 지원
- BERT 기반 감성 분석 데이터
"""
import os
import sys
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta
import json

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData, RegionalPriceStats
from apps.accounts.models import User

print("🚀 최종 더미 데이터 생성 시작")
print("=" * 60)

# 기존 데이터 정리
print("🧹 기존 데이터 정리 중...")
SentimentAnalysis.objects.all().delete()
PriceData.objects.all().delete()
RegionalPriceStats.objects.all().delete()
Review.objects.all().delete()
Clinic.objects.all().delete()

# 서울 지역구별 좌표 정보
DISTRICT_COORDINATES = {
    '강남구': {'lat': 37.5173, 'lng': 127.0473, 'center_lat': 37.5173, 'center_lng': 127.0473},
    '서초구': {'lat': 37.4837, 'lng': 127.0324, 'center_lat': 37.4837, 'center_lng': 127.0324},
    '송파구': {'lat': 37.5145, 'lng': 127.1059, 'center_lat': 37.5145, 'center_lng': 127.1059},
    '강동구': {'lat': 37.5301, 'lng': 127.1238, 'center_lat': 37.5301, 'center_lng': 127.1238},
    '마포구': {'lat': 37.5663, 'lng': 126.9019, 'center_lat': 37.5663, 'center_lng': 126.9019},
    '용산구': {'lat': 37.5326, 'lng': 126.9905, 'center_lat': 37.5326, 'center_lng': 126.9905},
    '성동구': {'lat': 37.5634, 'lng': 127.0371, 'center_lat': 37.5634, 'center_lng': 127.0371},
    '광진구': {'lat': 37.5384, 'lng': 127.0822, 'center_lat': 37.5384, 'center_lng': 127.0822},
    '종로구': {'lat': 37.5735, 'lng': 126.9788, 'center_lat': 37.5735, 'center_lng': 126.9788},
    '중구': {'lat': 37.5641, 'lng': 126.9979, 'center_lat': 37.5641, 'center_lng': 126.9979},
}

# 치과 이름 템플릿
CLINIC_PREFIXES = [
    "서울", "강남", "프리미엄", "모던", "스마일", "화이트", "브라이트", "클린", "베스트", "굿",
    "플러스", "엘리트", "VIP", "로얄", "골드", "다이아몬드", "플래티넘", "크리스탈", "실버", "펄",
    "럭셔리", "트렌드", "스타", "퍼펙트", "미소", "연세", "바른", "새로운", "행복한", "건강한",
    "아름다운", "밝은", "따뜻한", "친절한", "정성", "사랑", "희망", "꿈", "미래", "첨단",
    "현대", "신세계", "뉴", "탑", "원", "센터", "메디", "케어", "힐링", "웰니스"
]

CLINIC_SUFFIXES = [
    "치과", "치과의원", "치과병원", "덴탈클리닉", "덴탈센터", "구강클리닉", "치과센터"
]

def generate_clinic_name(district):
    """치과 이름 생성"""
    prefix = random.choice(CLINIC_PREFIXES)
    suffix = random.choice(CLINIC_SUFFIXES)
    
    # 지역명을 포함할 확률 30%
    if random.random() < 0.3:
        return f"{district} {prefix}{suffix}"
    else:
        return f"{prefix}{suffix}"

# 치료별 가격 범위 (원)
TREATMENT_PRICES = {
    'scaling': {'min': 15000, 'max': 35000, 'avg': 25000},
    'implant': {'min': 800000, 'max': 1500000, 'avg': 1100000},
    'root_canal': {'min': 150000, 'max': 400000, 'avg': 250000},
    'orthodontics': {'min': 3000000, 'max': 8000000, 'avg': 5000000},
    'whitening': {'min': 200000, 'max': 600000, 'avg': 350000},
    'extraction': {'min': 50000, 'max': 200000, 'avg': 100000},
    'filling': {'min': 80000, 'max': 250000, 'avg': 150000},
    'crown': {'min': 400000, 'max': 1200000, 'avg': 700000},
    'bridge': {'min': 800000, 'max': 2000000, 'avg': 1200000},
    'denture': {'min': 500000, 'max': 3000000, 'avg': 1500000},
}

# 리뷰 템플릿 (측면별)
REVIEW_TEMPLATES = {
    'positive': {
        'price': [
            "가격이 정말 합리적이에요. 다른 곳보다 저렴하면서도 치료 품질은 좋았습니다.",
            "비용 부담 없이 치료받을 수 있어서 좋았어요. 가성비 최고입니다.",
            "보험 적용도 잘 해주시고 추가 비용 없이 깔끔하게 치료해주셨어요.",
            "다른 치과보다 20% 정도 저렴한 것 같아요. 할인 이벤트도 자주 해서 좋습니다."
        ],
        'skill': [
            "원장님 실력이 정말 뛰어나세요. 아프지 않게 꼼꼼히 치료해주셨습니다.",
            "경험이 많으신 것 같아요. 정확한 진단과 치료로 만족스럽습니다.",
            "전문적이고 숙련된 솜씨로 치료받았어요. 결과가 완벽합니다.",
            "의료진 실력이 훌륭해요. 신중하고 정확하게 치료해주십니다."
        ],
        'kindness': [
            "직원분들이 모두 친절하세요. 따뜻하게 맞이해주셔서 기분 좋았어요.",
            "상냥하고 배려심 많은 서비스를 받았습니다. 정말 감사해요.",
            "예의 바르고 정중한 응대에 감동받았어요. 미소가 아름다우세요.",
            "친절한 설명과 세심한 배려로 편안하게 치료받았습니다."
        ],
        'waiting_time': [
            "대기시간이 거의 없어요. 예약 시간에 맞춰 바로 치료받았습니다.",
            "신속하고 빠른 진료로 시간 절약이 되었어요. 효율적입니다.",
            "정시에 시작해서 빨리 끝났어요. 시간 관리가 잘 되어 있습니다.",
            "즉시 치료받을 수 있어서 좋았어요. 대기 스트레스가 없었습니다."
        ],
        'facility': [
            "시설이 정말 깨끗하고 현대적이에요. 최신 장비로 치료받았습니다.",
            "위생 관리가 철저하고 소독도 잘 되어 있어서 안심됩니다.",
            "첨단 장비와 쾌적한 환경에서 치료받았어요. 시설이 훌륭합니다.",
            "넓고 깔끔한 진료실에서 편안하게 치료받았습니다."
        ],
        'overtreatment': [
            "필요한 치료만 정확히 해주셔서 신뢰가 갑니다. 과잉진료 없어요.",
            "정직하고 양심적인 진료를 받았어요. 불필요한 치료 권유 없습니다.",
            "꼭 필요한 것만 치료해주시고 자세히 설명해주셔서 좋았어요.",
            "적절한 치료 계획으로 과도한 비용 부담 없이 치료받았습니다."
        ]
    },
    'negative': {
        'price': [
            "가격이 너무 비싸요. 다른 곳보다 2배 정도 비싼 것 같아요.",
            "비용 부담이 커서 치료를 망설이게 됩니다. 바가지 쓴 기분이에요.",
            "보험 적용이 안 되는 항목이 많아서 돈이 많이 들었어요.",
            "추가 비용이 계속 발생해서 예상보다 훨씬 많이 나왔습니다."
        ],
        'skill': [
            "치료가 대충 된 것 같아요. 아직도 아프고 불편합니다.",
            "실력이 부족한 것 같아요. 치료 후에도 문제가 계속 생겨요.",
            "미숙한 솜씨로 치료받은 것 같아서 불안해요. 재치료가 필요할 듯해요.",
            "급하게 치료하신 것 같아요. 꼼꼼하지 못한 느낌입니다."
        ],
        'kindness': [
            "직원들이 불친절해요. 차갑고 무뚝뚝한 응대를 받았습니다.",
            "무례하고 성의 없는 서비스였어요. 기분이 나빴습니다.",
            "말투가 거칠고 배려가 부족해요. 환자를 대하는 태도가 아쉬워요.",
            "불쾌한 응대로 다시 가고 싶지 않아요. 서비스 교육이 필요해 보입니다."
        ],
        'waiting_time': [
            "대기시간이 너무 길어요. 2시간 넘게 기다렸습니다.",
            "예약했는데도 한참 기다려야 해서 불편했어요. 시간 관리가 안 돼요.",
            "느린 진료로 하루 종일 병원에 있었어요. 비효율적입니다.",
            "지연이 심해서 다른 일정에 차질이 생겼어요. 개선이 필요해요."
        ],
        'facility': [
            "시설이 낡고 더러워요. 위생 상태가 좋지 않은 것 같아요.",
            "구식 장비로 치료받아서 불안했어요. 시설 개선이 필요합니다.",
            "좁고 불편한 진료실이에요. 환경이 쾌적하지 않아요.",
            "소독이 제대로 안 된 것 같아서 걱정됩니다. 청결하지 못해요."
        ],
        'overtreatment': [
            "불필요한 치료를 계속 권유해요. 과잉진료 의심됩니다.",
            "억지로 비싼 치료를 강요하는 느낌이에요. 상술이 심해요.",
            "꼭 필요하지 않은 치료까지 추천해서 부담스러워요.",
            "과도한 치료 계획으로 비용이 너무 많이 나올 것 같아요."
        ]
    }
}

def generate_random_coordinate(district):
    """지역구 내 랜덤 좌표 생성"""
    base_coord = DISTRICT_COORDINATES[district]
    
    # 지역구 내에서 ±0.01도 범위 내 랜덤 좌표
    lat_offset = random.uniform(-0.01, 0.01)
    lng_offset = random.uniform(-0.01, 0.01)
    
    return {
        'lat': base_coord['lat'] + lat_offset,
        'lng': base_coord['lng'] + lng_offset
    }

def create_clinics():
    """치과 생성"""
    print("🏥 치과 데이터 생성 중...")
    
    clinics = []
    
    for district, coords in DISTRICT_COORDINATES.items():
        # 각 지역구당 10개 치과 (더 많이)
        for i in range(10):

                
            coord = generate_random_coordinate(district)
            
            # 편의시설 차별화
            facilities = {
                'has_parking': random.choice([True, False]),
                'night_service': random.choice([True, False]),
                'weekend_service': random.choice([True, False]),
            }
            
            # 지역별 특성 반영
            if district in ['강남구', '서초구']:  # 고급 지역
                facilities['has_parking'] = True
                facilities['night_service'] = True
            elif district in ['마포구', '용산구']:  # 젊은 지역
                facilities['weekend_service'] = True
            
            clinic_name = generate_clinic_name(district)
            
            clinic = Clinic.objects.create(
                name=clinic_name,
                district=district,
                address=f'서울특별시 {district} {random.choice(["테헤란로", "강남대로", "논현로", "선릉로", "역삼로"])} {random.randint(1, 200)}',
                phone=f'02-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}',
                latitude=Decimal(str(round(coord['lat'], 6))),
                longitude=Decimal(str(round(coord['lng'], 6))),
                has_parking=facilities['has_parking'],
                night_service=facilities['night_service'],
                weekend_service=facilities['weekend_service'],
                is_verified=True,
                description=f'{district}에 위치한 {clinic_name}입니다. 전문적인 치과 진료를 제공합니다.',
                specialties=random.choice([
                    '일반치과, 예방치료, 보존치료',
                    '임플란트, 보철치료, 구강외과',
                    '교정치과, 심미치료, 미백',
                    '소아치과, 예방치료, 불소도포',
                    '치주치료, 잇몸치료, 스케일링'
                ])
            )
            
            clinics.append(clinic)
            
            print(f"  ✅ {clinic.name} ({district}) - 주차:{facilities['has_parking']}, 야간:{facilities['night_service']}, 주말:{facilities['weekend_service']}")
    
    print(f"✅ 총 {len(clinics)}개 치과 생성 완료")
    return clinics

def create_reviews_and_analysis(clinics):
    """리뷰 및 감성 분석 데이터 생성"""
    print("📝 리뷰 및 감성 분석 데이터 생성 중...")
    
    total_reviews = 0
    
    for clinic in clinics:
        # 각 치과당 30-60개 리뷰 (더 많이)
        review_count = random.randint(30, 60)
        
        for i in range(review_count):
            # 긍정/부정 비율 (70% 긍정)
            is_positive = random.random() < 0.7
            sentiment_type = 'positive' if is_positive else 'negative'
            
            # 랜덤 측면 선택 (1-3개)
            aspects = random.sample(list(REVIEW_TEMPLATES[sentiment_type].keys()), 
                                  random.randint(1, 3))
            
            # 리뷰 텍스트 생성
            review_parts = []
            for aspect in aspects:
                template = random.choice(REVIEW_TEMPLATES[sentiment_type][aspect])
                review_parts.append(template)
            
            review_text = ' '.join(review_parts)
            
            # 평점 (긍정: 4-5점, 부정: 1-3점)
            if is_positive:
                rating = random.randint(4, 5)
            else:
                rating = random.randint(1, 3)
            
            # 리뷰 생성
            review = Review.objects.create(
                clinic=clinic,
                source='dummy',
                original_text=review_text,
                processed_text=review_text,
                original_rating=rating,
                reviewer_hash=f"dummy_user_{random.randint(10000, 99999)}",
                external_id=f"{clinic.id}_dummy_{i}_{int(datetime.now().timestamp())}",
                is_processed=True,
                review_date=timezone.now() - timedelta(days=random.randint(1, 365))
            )
            
            # 감성 분석 데이터 생성
            aspect_scores = {}
            for aspect in ['price', 'skill', 'kindness', 'waiting_time', 'facility', 'overtreatment']:
                if aspect in aspects:
                    # 해당 측면이 언급된 경우
                    if is_positive:
                        score = random.uniform(0.3, 0.9)
                    else:
                        score = random.uniform(-0.8, -0.2)
                else:
                    # 언급되지 않은 측면은 중립적
                    score = random.uniform(-0.2, 0.2)
                
                aspect_scores[aspect] = score
            
            # 감성 분석 결과 저장
            SentimentAnalysis.objects.create(
                review=review,
                price_score=Decimal(str(round(aspect_scores['price'], 2))),
                skill_score=Decimal(str(round(aspect_scores['skill'], 2))),
                kindness_score=Decimal(str(round(aspect_scores['kindness'], 2))),
                waiting_time_score=Decimal(str(round(aspect_scores['waiting_time'], 2))),
                facility_score=Decimal(str(round(aspect_scores['facility'], 2))),
                overtreatment_score=Decimal(str(round(aspect_scores['overtreatment'], 2))),
                model_version='bert_dummy_v1.0',
                confidence_score=Decimal(str(round(random.uniform(0.7, 0.95), 2)))
            )
            
            total_reviews += 1
        
        # 치과 통계 업데이트
        clinic.total_reviews = review_count
        avg_rating = Review.objects.filter(clinic=clinic).aggregate(
            avg=django.db.models.Avg('original_rating')
        )['avg']
        clinic.average_rating = Decimal(str(round(avg_rating, 2)))
        clinic.save()
        
        print(f"  ✅ {clinic.name}: {review_count}개 리뷰 생성")
    
    print(f"✅ 총 {total_reviews}개 리뷰 및 감성 분석 완료")

def create_price_data(clinics):
    """가격 데이터 생성"""
    print("💰 가격 데이터 생성 중...")
    
    total_prices = 0
    
    for clinic in clinics:
        # 각 치과당 5-8개 치료의 가격 정보
        treatments = random.sample(list(TREATMENT_PRICES.keys()), random.randint(5, 8))
        
        for treatment in treatments:
            price_info = TREATMENT_PRICES[treatment]
            
            # 지역별 가격 차이 반영 (더 다양하게)
            if clinic.district in ['강남구', '서초구']:  # 고급 지역 +20~50%
                multiplier = random.uniform(1.2, 1.5)
            elif clinic.district in ['송파구', '강동구']:  # 중간 지역 +10~30%
                multiplier = random.uniform(1.1, 1.3)
            elif clinic.district in ['마포구', '용산구']:  # 중간 지역 +5~25%
                multiplier = random.uniform(1.05, 1.25)
            else:  # 기타 지역 -10~+15%
                multiplier = random.uniform(0.9, 1.15)
            
            # 치과별 개별 차이 ±30% (더 큰 차이)
            individual_multiplier = random.uniform(0.7, 1.3)
            
            # 치과 등급별 차이 (이름 기반으로 추정)
            clinic_name = clinic.name.lower()
            if any(word in clinic_name for word in ['프리미엄', '럭셔리', 'vip', '다이아몬드', '플래티넘']):
                grade_multiplier = random.uniform(1.3, 1.8)  # 프리미엄 +30~80%
            elif any(word in clinic_name for word in ['엘리트', '로얄', '골드', '스타']):
                grade_multiplier = random.uniform(1.1, 1.4)  # 고급 +10~40%
            elif any(word in clinic_name for word in ['베스트', '굿', '플러스']):
                grade_multiplier = random.uniform(0.9, 1.2)  # 일반 -10~+20%
            else:
                grade_multiplier = random.uniform(0.8, 1.1)  # 기본 -20~+10%
            
            base_price = price_info['avg']
            final_price = int(base_price * multiplier * individual_multiplier * grade_multiplier)
            
            # 최소/최대 범위 내로 제한
            final_price = max(price_info['min'], min(price_info['max'], final_price))
            
            # 가격을 천원 단위로 반올림
            final_price = round(final_price / 1000) * 1000
            
            # 가격 데이터 생성
            PriceData.objects.create(
                clinic=clinic,
                treatment_type=treatment,
                price=final_price,
                currency='KRW',
                extraction_confidence=Decimal(str(round(random.uniform(0.8, 0.95), 2))),
                extraction_method='dummy_generation',
                is_verified=True,
                is_outlier=False
            )
            
            total_prices += 1
        
        print(f"  ✅ {clinic.name}: {len(treatments)}개 치료 가격 생성")
    
    print(f"✅ 총 {total_prices}개 가격 데이터 생성 완료")

def create_regional_stats():
    """지역별 가격 통계 생성"""
    print("📊 지역별 가격 통계 생성 중...")
    
    for district in DISTRICT_COORDINATES.keys():
        for treatment in TREATMENT_PRICES.keys():
            # 해당 지역, 치료의 가격 데이터 조회
            prices = PriceData.objects.filter(
                clinic__district=district,
                treatment_type=treatment,
                is_verified=True,
                is_outlier=False
            ).values_list('price', flat=True)
            
            if prices:
                prices_list = list(prices)
                prices_list.sort()
                
                min_price = min(prices_list)
                max_price = max(prices_list)
                avg_price = sum(prices_list) / len(prices_list)
                
                # 중간값 계산
                n = len(prices_list)
                if n % 2 == 0:
                    median_price = (prices_list[n//2-1] + prices_list[n//2]) / 2
                else:
                    median_price = prices_list[n//2]
                
                RegionalPriceStats.objects.create(
                    district=district,
                    treatment_type=treatment,
                    min_price=min_price,
                    max_price=max_price,
                    avg_price=Decimal(str(round(avg_price, 2))),
                    median_price=int(median_price),
                    sample_count=len(prices_list)
                )
        
        print(f"  ✅ {district} 가격 통계 생성 완료")
    
    print("✅ 지역별 가격 통계 생성 완료")

def create_test_users():
    """테스트 사용자 생성"""
    print("👤 테스트 사용자 생성 중...")
    
    # 관리자 계정
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@dentalai.com',
            password='admin123!',
            name='관리자'
        )
        print("  ✅ 관리자 계정 생성: admin / admin123!")
    
    # 일반 사용자 계정들
    test_users = [
        {'username': 'testuser1', 'email': 'test1@example.com', 'name': '김철수'},
        {'username': 'testuser2', 'email': 'test2@example.com', 'name': '이영희'},
        {'username': 'testuser3', 'email': 'test3@example.com', 'name': '박민수'},
    ]
    
    for user_data in test_users:
        if not User.objects.filter(username=user_data['username']).exists():
            User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password='test123!',
                name=user_data['name']
            )
            print(f"  ✅ 사용자 생성: {user_data['username']} / test123!")
    
    print("✅ 테스트 사용자 생성 완료")

def main():
    """메인 실행 함수"""
    try:
        # 1. 테스트 사용자 생성
        create_test_users()
        
        # 2. 치과 생성
        clinics = create_clinics()
        
        # 3. 리뷰 및 감성 분석 데이터 생성
        create_reviews_and_analysis(clinics)
        
        # 4. 가격 데이터 생성
        create_price_data(clinics)
        
        # 5. 지역별 통계 생성
        create_regional_stats()
        
        print("=" * 60)
        print("✅ 최종 더미 데이터 생성 완료!")
        print(f"📊 생성된 데이터:")
        print(f"   - 치과: {Clinic.objects.count()}개")
        print(f"   - 리뷰: {Review.objects.count()}개")
        print(f"   - 감성분석: {SentimentAnalysis.objects.count()}개")
        print(f"   - 가격데이터: {PriceData.objects.count()}개")
        print(f"   - 지역통계: {RegionalPriceStats.objects.count()}개")
        print(f"   - 사용자: {User.objects.count()}개")
        print("=" * 60)
        
        # 샘플 데이터 출력
        print("\n📋 샘플 데이터:")
        sample_clinic = Clinic.objects.first()
        if sample_clinic:
            print(f"치과: {sample_clinic.name} ({sample_clinic.district})")
            print(f"좌표: {sample_clinic.latitude}, {sample_clinic.longitude}")
            print(f"편의시설: 주차({sample_clinic.has_parking}), 야간({sample_clinic.night_service}), 주말({sample_clinic.weekend_service})")
            
            sample_review = Review.objects.filter(clinic=sample_clinic).first()
            if sample_review:
                print(f"리뷰: {sample_review.original_text[:100]}...")
                
                sentiment = SentimentAnalysis.objects.filter(review=sample_review).first()
                if sentiment:
                    print(f"감성분석: 가격({sentiment.price_score}), 실력({sentiment.skill_score})")
        
        print("\n🚀 서버를 시작하세요:")
        print("   python manage.py runserver")
        print("   http://localhost:8000")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()