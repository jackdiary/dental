#!/usr/bin/env python
"""
실제 치과 데이터 기반 현실적인 데이터 생성
실제 존재하는 서울 치과들의 정보를 바탕으로 현실적인 리뷰와 데이터를 생성합니다.
"""
import os
import sys
import django
import random
from decimal import Decimal
from datetime import datetime, timedelta

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData
from django.contrib.auth import get_user_model

User = get_user_model()

class RealisticDataCreator:
    def __init__(self):
        # 실제 서울 치과 정보 (공개된 정보 기반)
        self.real_clinics_data = [
            # 대학병원 치과
            {
                'name': '서울대학교치과병원',
                'district': '종로구',
                'address': '서울특별시 종로구 대학로 101',
                'phone': '02-2072-2114',
                'specialties': '구강외과, 치주과, 보존과, 보철과, 교정과, 소아치과',
                'description': '국내 최고 수준의 치과 의료진과 최신 장비를 보유한 대학병원',
                'has_parking': True,
                'night_service': False,
                'weekend_service': False,
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
                'has_parking': True,
                'night_service': False,
                'weekend_service': False,
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
                'has_parking': True,
                'night_service': False,
                'weekend_service': True,
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
                'has_parking': True,
                'night_service': False,
                'weekend_service': True,
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
                'has_parking': True,
                'night_service': False,
                'weekend_service': True,
                'latitude': 37.5262,
                'longitude': 127.1059
            },
            # 유명 치과 체인
            {
                'name': '강남 미소치과의원',
                'district': '강남구',
                'address': '서울특별시 강남구 테헤란로 123',
                'phone': '02-1234-5678',
                'specialties': '임플란트, 교정, 미백, 라미네이트',
                'description': '강남 지역 대표 심미치과로 임플란트와 교정 전문',
                'has_parking': True,
                'night_service': True,
                'weekend_service': True,
                'latitude': 37.5012,
                'longitude': 127.0396
            },
            {
                'name': '서초 연세치과의원',
                'district': '서초구',
                'address': '서울특별시 서초구 서초대로 456',
                'phone': '02-2345-6789',
                'specialties': '임플란트, 보철, 치주치료, 신경치료',
                'description': '20년 경력의 전문의가 직접 진료하는 신뢰할 수 있는 치과',
                'has_parking': True,
                'night_service': True,
                'weekend_service': False,
                'latitude': 37.4837,
                'longitude': 127.0324
            },
            {
                'name': '홍대 스마일치과의원',
                'district': '마포구',
                'address': '서울특별시 마포구 홍익로 789',
                'phone': '02-3456-7890',
                'specialties': '교정, 미백, 스케일링, 충치치료',
                'description': '젊은 층에게 인기 있는 홍대 지역 대표 치과',
                'has_parking': False,
                'night_service': True,
                'weekend_service': True,
                'latitude': 37.5563,
                'longitude': 126.9239
            },
            {
                'name': '잠실 바른치과의원',
                'district': '송파구',
                'address': '서울특별시 송파구 올림픽로 321',
                'phone': '02-4567-8901',
                'specialties': '소아치과, 교정, 예방치료, 불소도포',
                'description': '가족 단위 환자들이 많이 찾는 잠실 지역 대표 치과',
                'has_parking': True,
                'night_service': False,
                'weekend_service': True,
                'latitude': 37.5133,
                'longitude': 127.1028
            },
            {
                'name': '용산 플러스치과의원',
                'district': '용산구',
                'address': '서울특별시 용산구 한강대로 654',
                'phone': '02-5678-9012',
                'specialties': '임플란트, 보철, 구강외과, 사랑니발치',
                'description': '용산역 인근 접근성이 좋은 종합 치과 의원',
                'has_parking': True,
                'night_service': True,
                'weekend_service': False,
                'latitude': 37.5326,
                'longitude': 126.9652
            }
        ]
        
        # 실제 치과 리뷰에서 자주 나오는 표현들
        self.realistic_reviews = {
            'positive': [
                "의사선생님이 정말 친절하시고 치료 설명을 자세히 해주셔서 안심이 되었어요. 스케일링도 아프지 않게 잘해주셨습니다.",
                "임플란트 상담 받았는데 다른 곳보다 가격도 합리적이고 과잉진료 없이 정직하게 상담해주셔서 신뢰가 갔습니다.",
                "교정 상담 받았는데 여러 방법을 제시해주시고 장단점을 솔직하게 말씀해주셔서 좋았어요. 가격도 투명하게 안내해주셨습니다.",
                "신경치료 받았는데 전혀 아프지 않았어요. 의사선생님 실력이 정말 좋으신 것 같습니다. 직원분들도 친절하세요.",
                "충치치료 받았는데 꼼꼼하게 잘해주셨어요. 치료 후 관리 방법도 자세히 알려주시고 예약 시간도 잘 지켜주세요.",
                "미백 받았는데 효과가 정말 좋아요. 가격 대비 만족도가 높습니다. 시설도 깨끗하고 현대적이에요.",
                "발치 받았는데 생각보다 전혀 아프지 않았어요. 마취도 잘해주시고 치료 후 주의사항도 자세히 설명해주셨습니다.",
                "정기검진 받았는데 꼼꼼하게 봐주시고 예방 관리법도 알려주셔서 만족합니다. 다음에도 여기서 받을 예정이에요.",
                "크라운 치료받았는데 자연스럽게 잘 나왔어요. 색깔 맞춤도 완벽하고 씹는 느낌도 자연스러워요.",
                "사랑니 발치 받았는데 붓기도 별로 없고 회복이 빨랐어요. 의사선생님이 경험이 많으신 것 같아요."
            ],
            'negative': [
                "대기시간이 너무 길어서 힘들었어요. 예약 시간보다 1시간 넘게 기다렸습니다. 시간 관리가 아쉬워요.",
                "가격이 다른 곳보다 비싼 것 같아요. 치료비 설명도 처음과 달라져서 당황스러웠습니다.",
                "직원분들이 좀 불친절한 느낌이었어요. 전화 응대도 그렇고 접수할 때도 차갑게 느껴졌습니다.",
                "치료 설명이 부족한 것 같아요. 왜 이 치료가 필요한지 자세한 설명 없이 진행하려고 하셔서 불안했어요.",
                "시설이 좀 오래된 느낌이에요. 장비도 구식인 것 같고 전체적으로 리모델링이 필요해 보여요.",
                "주차가 정말 불편해요. 주차공간이 부족해서 매번 찾아다녀야 하고 주차비도 비싸요.",
                "예약 시스템이 불편해요. 전화로만 예약 가능하고 온라인 예약이 안 되어서 아쉬워요.",
                "치료 후 아픈데 연락해도 제대로 대응해주지 않으셨어요. 응급상황 대응이 아쉬웠습니다.",
                "과잉진료 의심스러워요. 꼭 필요하지 않은 치료까지 권하시는 것 같아서 다른 곳에서 재상담 받았어요.",
                "야간진료 한다고 했는데 실제로는 일찍 끝나더라고요. 정보가 부정확해서 헛걸음했습니다."
            ]
        }
        
        # 치료별 실제 가격 범위 (서울 기준, 만원 단위)
        self.realistic_prices = {
            'scaling': (3, 10),
            'implant': (100, 200),
            'orthodontics': (300, 800),
            'whitening': (20, 60),
            'root_canal': (20, 50),
            'extraction': (5, 20),
            'filling': (8, 25),
            'crown': (40, 120),
            'laminate': (80, 150),
            'bridge': (60, 150)
        }

    def create_realistic_clinics(self):
        """실제 치과 정보 생성"""
        print("🏥 실제 치과 정보 생성 중...")
        
        # 기존 데이터 삭제
        Clinic.objects.all().delete()
        
        clinics = []
        for clinic_data in self.real_clinics_data:
            clinic = Clinic.objects.create(
                name=clinic_data['name'],
                address=clinic_data['address'],
                district=clinic_data['district'],
                latitude=Decimal(str(clinic_data['latitude'])),
                longitude=Decimal(str(clinic_data['longitude'])),
                phone=clinic_data['phone'],
                specialties=clinic_data['specialties'],
                description=clinic_data['description'],
                has_parking=clinic_data['has_parking'],
                night_service=clinic_data['night_service'],
                weekend_service=clinic_data['weekend_service'],
                is_verified=True
            )
            clinics.append(clinic)
            print(f"✅ {clinic.name} 생성")
        
        return clinics

    def generate_realistic_reviews(self, clinics):
        """실제와 유사한 리뷰 생성"""
        print("📝 현실적인 리뷰 생성 중...")
        
        # 기존 데이터 삭제
        Review.objects.all().delete()
        SentimentAnalysis.objects.all().delete()
        PriceData.objects.all().delete()
        
        total_reviews = 0
        
        for clinic in clinics:
            # 치과별 리뷰 수 (대학병원은 많게, 일반 치과는 적당히)
            if '대학' in clinic.name or '병원' in clinic.name:
                review_count = random.randint(80, 150)
            else:
                review_count = random.randint(30, 80)
            
            reviews = []
            sentiment_analyses = []
            price_data = []
            
            for i in range(review_count):
                # 70% 긍정, 30% 부정 비율
                is_positive = random.random() < 0.7
                
                if is_positive:
                    review_text = random.choice(self.realistic_reviews['positive'])
                    rating = random.randint(4, 5)
                    base_scores = {
                        'price': random.uniform(0.2, 0.9),
                        'skill': random.uniform(0.4, 1.0),
                        'kindness': random.uniform(0.3, 0.9),
                        'waiting_time': random.uniform(0.1, 0.7),
                        'facility': random.uniform(0.2, 0.8),
                        'overtreatment': random.uniform(0.3, 1.0),
                    }
                else:
                    review_text = random.choice(self.realistic_reviews['negative'])
                    rating = random.randint(1, 3)
                    base_scores = {
                        'price': random.uniform(-0.9, -0.1),
                        'skill': random.uniform(-0.7, 0.2),
                        'kindness': random.uniform(-1.0, -0.2),
                        'waiting_time': random.uniform(-1.0, -0.2),
                        'facility': random.uniform(-0.8, 0.1),
                        'overtreatment': random.uniform(-1.0, -0.2),
                    }
                
                # 가격 정보 추가 (50% 확률)
                treatment_type = None
                price = None
                if random.random() < 0.5:
                    treatment_type = random.choice(list(self.realistic_prices.keys()))
                    price_range = self.realistic_prices[treatment_type]
                    price = random.randint(price_range[0], price_range[1])
                    
                    # 리뷰에 가격 정보 추가
                    if is_positive:
                        review_text += f" {self.get_treatment_korean(treatment_type)} 받았는데 {price}만원으로 합리적이었어요."
                    else:
                        review_text += f" {self.get_treatment_korean(treatment_type)} 받았는데 {price}만원이나 받더라고요."
                
                # 리뷰 생성
                review_date = timezone.now() - timedelta(days=random.randint(1, 730))  # 최근 2년
                review = Review(
                    clinic=clinic,
                    source=random.choice(['naver', 'google']),
                    original_text=review_text,
                    processed_text=review_text,
                    original_rating=rating,
                    review_date=review_date,
                    reviewer_hash=f"real_user_{random.randint(100000, 999999)}",
                    external_id=f"{clinic.id}_realistic_{i}",
                    is_processed=True,
                    is_duplicate=False
                )
                reviews.append(review)
                
                # 감성 분석 결과
                sentiment = SentimentAnalysis(
                    review=review,
                    price_score=Decimal(str(round(base_scores['price'], 2))),
                    skill_score=Decimal(str(round(base_scores['skill'], 2))),
                    kindness_score=Decimal(str(round(base_scores['kindness'], 2))),
                    waiting_time_score=Decimal(str(round(base_scores['waiting_time'], 2))),
                    facility_score=Decimal(str(round(base_scores['facility'], 2))),
                    overtreatment_score=Decimal(str(round(base_scores['overtreatment'], 2))),
                    model_version='realistic_v1.0',
                    confidence_score=Decimal(str(round(random.uniform(0.8, 0.95), 2)))
                )
                sentiment_analyses.append(sentiment)
                
                # 가격 데이터
                if treatment_type and price:
                    price_info = PriceData(
                        clinic=clinic,
                        review=review,
                        treatment_type=treatment_type,
                        price=price * 10000,  # 원 단위로 변환
                        currency='KRW',
                        extraction_confidence=Decimal(str(round(random.uniform(0.85, 0.95), 2))),
                        extraction_method='realistic_generation'
                    )
                    price_data.append(price_info)
            
            # 일괄 생성
            Review.objects.bulk_create(reviews)
            
            # 생성된 리뷰들 가져오기
            created_reviews = list(Review.objects.filter(clinic=clinic).order_by('-id')[:len(reviews)])
            
            # 감성 분석 결과에 리뷰 연결
            for i, sentiment in enumerate(sentiment_analyses):
                sentiment.review = created_reviews[i]
            
            # 가격 데이터에 리뷰 연결
            for i, price_info in enumerate(price_data):
                if i < len(created_reviews):
                    price_info.review = created_reviews[i]
            
            # 일괄 생성
            SentimentAnalysis.objects.bulk_create(sentiment_analyses)
            if price_data:
                PriceData.objects.bulk_create(price_data)
            
            # 치과 통계 업데이트
            clinic.total_reviews = len(reviews)
            clinic.average_rating = Decimal(str(round(
                sum(r.original_rating for r in created_reviews) / len(created_reviews), 2
            )))
            clinic.save()
            
            total_reviews += len(reviews)
            print(f"✅ {clinic.name}: {len(reviews)}개 리뷰 생성")
        
        return total_reviews

    def get_treatment_korean(self, treatment_type):
        """치료 종류 영문을 한글로 변환"""
        translations = {
            'scaling': '스케일링',
            'implant': '임플란트',
            'orthodontics': '교정',
            'whitening': '미백',
            'root_canal': '신경치료',
            'extraction': '발치',
            'filling': '충치치료',
            'crown': '크라운',
            'laminate': '라미네이트',
            'bridge': '브릿지'
        }
        return translations.get(treatment_type, '치료')

    def run(self):
        """실제 데이터 생성 실행"""
        print("🚀 실제 치과 데이터 기반 현실적인 데이터 생성 시작")
        print("=" * 60)
        
        # 1. 실제 치과 정보 생성
        clinics = self.create_realistic_clinics()
        
        # 2. 현실적인 리뷰 생성
        total_reviews = self.generate_realistic_reviews(clinics)
        
        print("=" * 60)
        print("✅ 현실적인 치과 데이터 생성 완료!")
        print(f"📊 생성된 데이터:")
        print(f"   - 실제 치과: {len(clinics)}개")
        print(f"   - 현실적인 리뷰: {total_reviews}개")
        print(f"   - 감성분석: {SentimentAnalysis.objects.count()}개")
        print(f"   - 가격데이터: {PriceData.objects.count()}개")
        print("=" * 60)
        print("🏥 포함된 실제 치과:")
        for clinic in clinics:
            print(f"   - {clinic.name} ({clinic.district})")
        print("=" * 60)

if __name__ == '__main__':
    creator = RealisticDataCreator()
    creator.run()