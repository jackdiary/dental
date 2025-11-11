#!/usr/bin/env python
"""
대량의 치과 및 리뷰 데이터 생성 스크립트
기존 현실적인 데이터에 추가로 더 많은 데이터를 생성합니다.
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random
from django.utils import timezone

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData

class MassiveDataCreator:
    def __init__(self):
        # 서울시 전체 25개 자치구
        self.districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구',
            '광진구', '구로구', '금천구', '노원구', '도봉구',
            '동대문구', '동작구', '마포구', '서대문구', '서초구',
            '성동구', '성북구', '송파구', '양천구', '영등포구',
            '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
        
        # 치과 이름 패턴
        self.clinic_prefixes = [
            '서울', '강남', '신촌', '홍대', '잠실', '건대', '이대', '명동', '종로', '을지로',
            '압구정', '청담', '논현', '역삼', '삼성', '선릉', '강변', '천호', '길동', '둔촌',
            '성수', '왕십리', '청량리', '회기', '석계', '노원', '상계', '중계', '도봉', '창동',
            '수유', '미아', '정릉', '성북', '안암', '고려대', '연대', '서대문', '충정로', '시청',
            '을지로', '동대문', '신설동', '제기동', '청량리', '답십리', '장한평', '군자', '아차산',
            '광나루', '천호', '강동', '암사', '고덕', '상일동', '하남', '미사', '풍납토성'
        ]
        
        self.clinic_suffixes = [
            '치과의원', '치과병원', '덴탈클리닉', '치과', '스마일치과', '미소치과', '행복치과',
            '건강치과', '밝은치과', '새로운치과', '든든치과', '믿음치과', '정성치과', '친절치과',
            '전문치과', '우수치과', '최고치과', '안전치과', '깨끗한치과', '편안한치과',
            '정확한치과', '꼼꼼한치과', '세심한치과', '정직한치과', '프리미엄치과',
            '화이트치과', '플러스치과', '케어치과', '라이프치과', '헬스치과'
        ]
        
        # 치료 종류
        self.treatments = [
            '스케일링', '임플란트', '교정', '미백', '신경치료', '발치',
            '충치치료', '크라운', '브릿지', '틀니', '사랑니', '잇몸치료',
            '치주치료', '보철치료', '소아치과', '구강외과', '라미네이트',
            '인레이', '온레이', '베니어', '치아성형', '불소도포'
        ]
        
        # 리뷰 템플릿 (긍정적)
        self.positive_reviews = [
            "의사선생님이 정말 친절하시고 설명도 자세히 해주셔서 좋았어요. 치료 과정을 하나하나 설명해주시니 안심이 되었습니다.",
            "스케일링 받았는데 전혀 아프지 않게 해주셨어요. 직원분들도 친절하고 시설도 깨끗해서 만족합니다.",
            "임플란트 상담받았는데 다른 곳보다 가격도 합리적이고 설명이 자세해서 신뢰가 갔어요. 과잉진료 없이 정직하게 상담해주셨습니다.",
            "교정 상담 받았는데 여러 방법을 제시해주시고 장단점을 솔직하게 말씀해주셔서 좋았습니다. 가격도 투명하게 안내해주셨어요.",
            "신경치료 받았는데 아프지 않게 잘해주셨어요. 마취도 잘해주시고 치료 후 주의사항도 자세히 설명해주셨습니다.",
            "충치치료 받았는데 꼼꼼하게 잘해주셨어요. 치료 후 관리 방법도 자세히 알려주시고 예약 시간도 잘 지켜주세요.",
            "미백 받았는데 효과가 정말 좋아요. 가격 대비 만족도가 높습니다. 시설도 깨끗하고 현대적이에요.",
            "발치 받았는데 생각보다 전혀 아프지 않았어요. 의사선생님 실력이 정말 좋으신 것 같아요.",
            "정기검진 받았는데 꼼꼼하게 봐주시고 예방 관리법도 알려주셔서 만족합니다. 다음에도 여기서 받을 예정이에요.",
            "크라운 치료받았는데 자연스럽게 잘 나왔어요. 색깔 맞춤도 완벽하고 씹는 느낌도 자연스러워요.",
            "사랑니 발치 받았는데 붓기도 별로 없고 회복이 빨랐어요. 의사선생님이 경험이 많으신 것 같아요.",
            "브릿지 치료 받았는데 결과가 정말 만족스러워요. 자연치와 구별이 안 될 정도로 잘 만들어주셨어요.",
            "틀니 제작했는데 착용감이 정말 좋아요. 처음에는 어색했지만 금세 적응되었습니다.",
            "잇몸치료 받았는데 염증이 많이 좋아졌어요. 선생님이 정말 실력이 좋으세요.",
            "야간진료 가능해서 직장인에게 정말 좋아요. 늦은 시간에도 친절하게 진료해주십니다.",
            "라미네이트 받았는데 정말 자연스럽고 예뻐요. 가격도 다른 곳보다 합리적이었습니다.",
            "인레이 치료받았는데 정교하게 잘 만들어주셨어요. 씹는 느낌도 자연스럽고 만족합니다.",
            "소아치과 전문이라 아이가 무서워하지 않고 잘 받았어요. 선생님이 아이들을 잘 다루세요.",
            "구강외과 수술받았는데 회복이 빨랐어요. 수술 후 관리도 잘 해주셨습니다.",
            "불소도포 받았는데 아이가 충치 예방에 도움이 될 것 같아요. 정기적으로 받으러 올 예정입니다."
        ]
        
        # 부정적 리뷰 템플릿
        self.negative_reviews = [
            "가격이 너무 비싸요. 다른 곳보다 훨씬 비싸면서 서비스는 별로였어요.",
            "대기시간이 너무 길어서 힘들었어요. 예약 시간보다 1시간 넘게 기다렸습니다.",
            "과잉진료 의심스러워요. 꼭 필요하지 않은 치료까지 권하시는 것 같아요.",
            "직원분들이 불친절해요. 설명도 대충하시고 성의가 없어 보였습니다.",
            "시설이 좀 오래된 것 같아요. 장비도 구식인 것 같고 청결도가 아쉬워요.",
            "치료 후 아픈데 제대로 처치해주지 않으셨어요. 다시 가기 싫습니다.",
            "예약이 어려워요. 전화해도 잘 안 받으시고 일정 조정이 힘들어요.",
            "주차가 불편해요. 주차공간이 부족해서 매번 고생합니다.",
            "야간진료 한다고 했는데 실제로는 일찍 끝나더라고요. 정보가 부정확해요.",
            "가격 설명이 불명확해요. 처음 말씀하신 것과 나중에 청구된 금액이 달라요.",
            "치료 결과가 만족스럽지 않아요. 다른 곳에서 다시 받아야 할 것 같습니다.",
            "대기실이 너무 좁고 불편해요. 환경 개선이 필요할 것 같습니다.",
            "치료 설명이 부족한 것 같아요. 왜 이 치료가 필요한지 자세한 설명이 없었어요.",
            "응급상황 대응이 아쉬웠어요. 치료 후 문제가 생겼는데 제대로 대응해주지 않으셨어요.",
            "온라인 예약이 안 되어서 불편해요. 전화로만 예약 가능해서 아쉽습니다."
        ]
        
        # 치료별 가격 범위 (만원 단위)
        self.price_ranges = {
            '스케일링': (2, 10),
            '임플란트': (80, 250),
            '교정': (200, 1000),
            '미백': (10, 80),
            '신경치료': (15, 50),
            '발치': (3, 25),
            '충치치료': (5, 30),
            '크라운': (30, 150),
            '브릿지': (50, 200),
            '틀니': (100, 500),
            '사랑니': (5, 30),
            '잇몸치료': (10, 40),
            '치주치료': (20, 60),
            '보철치료': (40, 180),
            '소아치과': (3, 15),
            '구강외과': (20, 100),
            '라미네이트': (80, 200),
            '인레이': (15, 40),
            '온레이': (20, 50),
            '베니어': (60, 150),
            '치아성형': (30, 80),
            '불소도포': (1, 5)
        }

    def create_additional_clinics(self, count=500):
        """추가 치과 데이터 생성"""
        print(f"🏥 {count}개 추가 치과 데이터 생성 중...")
        
        existing_count = Clinic.objects.count()
        clinics = []
        
        for i in range(count):
            district = random.choice(self.districts)
            prefix = random.choice(self.clinic_prefixes)
            suffix = random.choice(self.clinic_suffixes)
            clinic_name = f"{prefix} {suffix}"
            
            # 중복 이름 방지
            counter = 1
            original_name = clinic_name
            while Clinic.objects.filter(name=clinic_name).exists():
                clinic_name = f"{original_name} {counter}호점"
                counter += 1
            
            # 지역별 대략적인 좌표 범위 (서울 기준)
            lat_base = 37.5665 + random.uniform(-0.2, 0.2)
            lng_base = 126.9780 + random.uniform(-0.2, 0.2)
            
            # 전문분야 설정 (3-10개 랜덤 선택)
            num_specialties = random.randint(3, 10)
            selected_treatments = random.sample(self.treatments, num_specialties)
            specialties = ', '.join(selected_treatments)
            
            clinic = Clinic(
                name=clinic_name,
                address=f"서울특별시 {district} {random.randint(1, 999)}번길 {random.randint(1, 200)}",
                district=district,
                latitude=Decimal(str(round(lat_base, 6))),
                longitude=Decimal(str(round(lng_base, 6))),
                phone=f"02-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                has_parking=random.choice([True, False]),
                night_service=random.choice([True, False]),
                weekend_service=random.choice([True, False]),
                specialties=specialties,
                description=f"{district}에 위치한 {clinic_name}입니다. {', '.join(selected_treatments[:3])} 전문 치과로 최신 장비와 숙련된 의료진을 보유하고 있습니다.",
                business_hours="평일 09:00-18:00, 토요일 09:00-13:00",
                is_verified=random.choice([True, False])
            )
            clinics.append(clinic)
        
        Clinic.objects.bulk_create(clinics)
        print(f"✅ {count}개 추가 치과 생성 완료 (총 {existing_count + count}개)")
        return Clinic.objects.all()

    def create_massive_reviews(self, clinics):
        """대량 리뷰 및 분석 데이터 생성"""
        print("📝 대량 리뷰 및 감성 분석 데이터 생성 중...")
        
        total_reviews = 0
        
        for clinic in clinics:
            # 기존 리뷰가 있는 치과는 건너뛰기
            if clinic.total_reviews and clinic.total_reviews > 0:
                continue
                
            # 치과별 리뷰 수 (5~200개, 가중치 적용)
            review_count = random.choices(
                [
                    random.randint(5, 20),    # 소규모 치과
                    random.randint(20, 50),   # 중간 규모 치과
                    random.randint(50, 100),  # 큰 치과
                    random.randint(100, 200)  # 대형 치과/병원
                ],
                weights=[50, 30, 15, 5]
            )[0]
            
            reviews = []
            sentiment_analyses = []
            price_data = []
            
            for _ in range(review_count):
                # 긍정/부정 리뷰 비율 (70% 긍정)
                is_positive = random.random() < 0.7
                
                if is_positive:
                    review_text = random.choice(self.positive_reviews)
                    base_scores = {
                        'price': random.uniform(0.1, 1.0),
                        'skill': random.uniform(0.2, 1.0),
                        'kindness': random.uniform(0.1, 1.0),
                        'waiting_time': random.uniform(0.0, 0.9),
                        'facility': random.uniform(0.1, 1.0),
                        'overtreatment': random.uniform(0.2, 1.0),
                    }
                    rating = random.choices([3, 4, 5], weights=[15, 35, 50])[0]
                else:
                    review_text = random.choice(self.negative_reviews)
                    base_scores = {
                        'price': random.uniform(-1.0, 0.0),
                        'skill': random.uniform(-1.0, 0.2),
                        'kindness': random.uniform(-1.0, 0.0),
                        'waiting_time': random.uniform(-1.0, -0.1),
                        'facility': random.uniform(-1.0, 0.1),
                        'overtreatment': random.uniform(-1.0, -0.1),
                    }
                    rating = random.choices([1, 2, 3], weights=[40, 40, 20])[0]
                
                # 가격 정보 추가 (40% 확률)
                treatment_type = None
                price = None
                if random.random() < 0.4:
                    # 치과의 전문분야 중에서 선택
                    clinic_treatments = [t.strip() for t in clinic.specialties.split(',')]
                    available_treatments = [t for t in clinic_treatments if t in self.price_ranges]
                    
                    if available_treatments:
                        treatment_type = random.choice(available_treatments)
                        price_range = self.price_ranges[treatment_type]
                        price = random.randint(price_range[0], price_range[1])
                        
                        # 리뷰에 가격 정보 추가
                        if is_positive:
                            review_text += f" {treatment_type} 받았는데 {price}만원으로 합리적이었어요."
                        else:
                            review_text += f" {treatment_type} 받았는데 {price}만원이나 받더라고요."
                
                # 리뷰 생성
                review_date = timezone.now() - timedelta(days=random.randint(1, 1095))  # 3년 범위
                external_id = f"{clinic.id}_{random.randint(100000, 999999)}_{len(reviews)}"
                review = Review(
                    clinic=clinic,
                    source=random.choice(['naver', 'google', 'kakao']),
                    original_text=review_text,
                    processed_text=review_text,
                    original_rating=rating,
                    review_date=review_date,
                    reviewer_hash=f"user_{random.randint(10000, 999999)}",
                    external_id=external_id,
                    is_processed=True,
                    is_duplicate=False
                )
                reviews.append(review)
                
                # 감성 분석 결과 생성
                sentiment = SentimentAnalysis(
                    review=review,
                    price_score=Decimal(str(round(base_scores['price'], 2))),
                    skill_score=Decimal(str(round(base_scores['skill'], 2))),
                    kindness_score=Decimal(str(round(base_scores['kindness'], 2))),
                    waiting_time_score=Decimal(str(round(base_scores['waiting_time'], 2))),
                    facility_score=Decimal(str(round(base_scores['facility'], 2))),
                    overtreatment_score=Decimal(str(round(base_scores['overtreatment'], 2))),
                    model_version='massive_v1.0',
                    confidence_score=Decimal(str(round(random.uniform(0.70, 0.99), 2)))
                )
                sentiment_analyses.append(sentiment)
                
                # 가격 데이터 생성
                if treatment_type and price:
                    price_info = PriceData(
                        clinic=clinic,
                        review=review,
                        treatment_type=treatment_type,
                        price=price * 10000,  # 원 단위로 변환
                        currency='KRW',
                        extraction_confidence=Decimal(str(round(random.uniform(0.80, 0.99), 2))),
                        extraction_method='regex'
                    )
                    price_data.append(price_info)
            
            # 리뷰 일괄 생성
            Review.objects.bulk_create(reviews)
            
            # 생성된 리뷰들 가져오기
            created_reviews = list(Review.objects.filter(clinic=clinic).order_by('-id')[:len(reviews)])
            
            # 감성 분석 결과에 리뷰 연결
            for i, sentiment in enumerate(sentiment_analyses):
                sentiment.review = created_reviews[i]
            
            # 가격 데이터에 리뷰 연결
            for i, review in enumerate(created_reviews):
                if i < len(price_data):
                    price_data[i].review = review
            
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
            
            if total_reviews % 1000 == 0:
                print(f"  진행상황: {total_reviews}개 리뷰 생성 완료...")
        
        print(f"✅ 총 {total_reviews}개 추가 리뷰 및 분석 데이터 생성 완료")

    def run(self):
        """대량 데이터 생성 실행"""
        print("🚀 대량 치과 및 리뷰 데이터 생성 시작...")
        print("=" * 80)
        
        # 현재 데이터 현황
        print(f"현재 치과 수: {Clinic.objects.count()}개")
        print(f"현재 리뷰 수: {Review.objects.count()}개")
        print()
        
        # 1. 추가 치과 데이터 생성 (500개)
        clinics = self.create_additional_clinics(500)
        
        # 2. 대량 리뷰 및 분석 데이터 생성
        self.create_massive_reviews(clinics)
        
        print("=" * 80)
        print("✅ 대량 치과 및 리뷰 데이터 생성 완료!")
        print(f"📊 최종 데이터:")
        print(f"   - 총 치과: {Clinic.objects.count()}개")
        print(f"   - 총 리뷰: {Review.objects.count()}개")
        print(f"   - 총 감성분석: {SentimentAnalysis.objects.count()}개")
        print(f"   - 총 가격데이터: {PriceData.objects.count()}개")
        print("=" * 80)

if __name__ == '__main__':
    creator = MassiveDataCreator()
    creator.run()