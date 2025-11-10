#!/usr/bin/env python
"""
통합된 더미 데이터 생성 스크립트
전체 서비스에서 일관성 있게 사용할 수 있는 데이터를 생성합니다.
"""
import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
import random
from django.utils import timezone

# Django 설정
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData
from django.contrib.auth import get_user_model

User = get_user_model()

class UnifiedDataCreator:
    def __init__(self):
        # 서울시 전체 25개 자치구
        self.districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구',
            '광진구', '구로구', '금천구', '노원구', '도봉구',
            '동대문구', '동작구', '마포구', '서대문구', '서초구',
            '성동구', '성북구', '송파구', '양천구', '영등포구',
            '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
        
        # 치료 종류 (한국어)
        self.treatment_types = [
            '스케일링', '임플란트', '교정', '미백', '신경치료', '발치',
            '충치치료', '크라운', '브릿지', '틀니', '사랑니', '잇몸치료',
            '치주치료', '보철치료', '소아치과', '구강외과'
        ]
        
        # 치과 이름 템플릿
        self.clinic_names = [
            '서울치과의원', '미소치과', '행복치과', '건강치과', '밝은치과',
            '새로운치과', '든든치과', '믿음치과', '정성치과', '친절치과',
            '전문치과', '우수치과', '최고치과', '안전치과', '깨끗한치과',
            '편안한치과', '정확한치과', '꼼꼼한치과', '세심한치과', '정직한치과',
            '프리미엄치과', '스마일치과', '화이트치과', '플러스치과', '케어치과'
        ]
        
        # 실제 리뷰 템플릿 (긍정적)
        self.positive_reviews = [
            "의사선생님이 정말 친절하시고 설명도 자세히 해주셔서 좋았어요. 가격도 합리적이고 과잉진료 없이 필요한 치료만 해주셨습니다.",
            "스케일링 받았는데 {price}만원으로 저렴했어요. 직원분들도 친절하고 시설도 깨끗합니다.",
            "임플란트 상담받았는데 다른 곳보다 {price}만원 정도 저렴하면서도 설명이 자세해서 신뢰가 갔어요.",
            "교정 상담 받았는데 과잉진료 없이 정직하게 상담해주셔서 좋았습니다. 가격도 {price}만원으로 합리적이에요.",
            "신경치료 받았는데 아프지 않게 잘해주셨어요. {price}만원으로 다른 곳보다 저렴했습니다.",
            "충치치료 받았는데 꼼꼼하게 잘해주셨어요. 가격도 {price}만원으로 부담없었습니다.",
            "발치 받았는데 전혀 아프지 않았어요. 의사선생님 실력이 정말 좋으신 것 같아요.",
            "미백 받았는데 효과가 정말 좋아요. {price}만원으로 가성비 최고입니다.",
            "크라운 치료받았는데 자연스럽게 잘 나왔어요. 가격도 {price}만원으로 합리적이었습니다.",
            "정기검진 받았는데 꼼꼼하게 봐주시고 설명도 자세히 해주셔서 만족합니다.",
            "브릿지 치료 받았는데 {price}만원으로 다른 곳보다 저렴하고 결과도 만족스러워요.",
            "틀니 제작했는데 착용감이 정말 좋아요. 가격도 {price}만원으로 합리적이었습니다.",
            "사랑니 발치했는데 빠르고 아프지 않게 해주셨어요. 추천합니다.",
            "잇몸치료 받았는데 염증이 많이 좋아졌어요. 선생님이 정말 실력이 좋으세요.",
            "야간진료 가능해서 직장인에게 정말 좋아요. 늦은 시간에도 친절하게 진료해주십니다."
        ]
        
        # 부정적 리뷰 템플릿
        self.negative_reviews = [
            "가격이 너무 비싸요. {price}만원이나 받으면서 서비스는 별로였어요.",
            "대기시간이 너무 길어서 힘들었어요. 예약 시간을 지켜주셨으면 좋겠어요.",
            "과잉진료 의심스러워요. 꼭 필요하지 않은 치료까지 권하시는 것 같아요.",
            "직원분들이 불친절해요. 설명도 대충하시고 성의가 없어 보였습니다.",
            "시설이 좀 오래된 것 같아요. 장비도 구식인 것 같고 청결도가 아쉬워요.",
            "치료 후 아픈데 제대로 처치해주지 않으셨어요. 다시 가기 싫습니다.",
            "예약이 어려워요. 전화해도 잘 안 받으시고 일정 조정이 힘들어요.",
            "주차가 불편해요. 주차공간이 부족해서 매번 고생합니다.",
            "야간진료 한다고 했는데 실제로는 일찍 끝나더라고요. 정보가 부정확해요.",
            "가격 설명이 불명확해요. 처음 말씀하신 것과 나중에 청구된 금액이 달라요.",
            "치료 결과가 만족스럽지 않아요. 다른 곳에서 다시 받아야 할 것 같습니다.",
            "대기실이 너무 좁고 불편해요. 환경 개선이 필요할 것 같습니다."
        ]
        
        # 치료별 가격 범위 (만원 단위)
        self.price_ranges = {
            '스케일링': (2, 8),
            '임플란트': (80, 200),
            '교정': (200, 800),
            '미백': (10, 50),
            '신경치료': (15, 40),
            '발치': (3, 15),
            '충치치료': (5, 20),
            '크라운': (30, 100),
            '브릿지': (50, 150),
            '틀니': (100, 400),
            '사랑니': (5, 20),
            '잇몸치료': (10, 30)
        }

    def create_admin_user(self):
        """관리자 계정 생성"""
        if not User.objects.filter(email='admin@dental.com').exists():
            admin = User.objects.create_superuser(
                email='admin@dental.com',
                username='admin',
                password='admin123!@#'
            )
            print(f"✅ 관리자 계정 생성: {admin.email}")
        else:
            print("✅ 관리자 계정이 이미 존재합니다.")

    def create_test_users(self):
        """테스트 사용자 계정들 생성"""
        test_users = [
            {'email': 'user1@test.com', 'username': 'testuser1', 'password': 'test123!@#'},
            {'email': 'user2@test.com', 'username': 'testuser2', 'password': 'test123!@#'},
            {'email': 'user3@test.com', 'username': 'testuser3', 'password': 'test123!@#'},
        ]
        
        for user_data in test_users:
            if not User.objects.filter(email=user_data['email']).exists():
                user = User.objects.create_user(**user_data)
                print(f"✅ 테스트 사용자 생성: {user.email}")

    def create_clinics(self, count=200):
        """통합된 치과 데이터 생성"""
        print(f"🏥 {count}개 치과 데이터 생성 중...")
        
        # 기존 데이터 삭제
        Clinic.objects.all().delete()
        
        clinics = []
        for i in range(count):
            district = random.choice(self.districts)
            clinic_name = f"{district} {random.choice(self.clinic_names)}"
            
            # 지역별 대략적인 좌표 범위 (서울 기준)
            lat_base = 37.5665 + random.uniform(-0.15, 0.15)
            lng_base = 126.9780 + random.uniform(-0.15, 0.15)
            
            # 전문분야 설정 (3-8개 랜덤 선택)
            num_specialties = random.randint(3, 8)
            selected_treatments = random.sample(self.treatment_types, num_specialties)
            specialties = ', '.join(selected_treatments)
            
            clinic = Clinic(
                name=clinic_name,
                address=f"서울특별시 {district} {random.randint(1, 999)}번길 {random.randint(1, 100)}",
                district=district,
                latitude=Decimal(str(round(lat_base, 6))),
                longitude=Decimal(str(round(lng_base, 6))),
                phone=f"02-{random.randint(1000, 9999)}-{random.randint(1000, 9999)}",
                has_parking=random.choice([True, False]),
                night_service=random.choice([True, False]),
                weekend_service=random.choice([True, False]),
                specialties=specialties,
                description=f"{district}에 위치한 {clinic_name}입니다. {', '.join(selected_treatments[:3])} 전문 치과입니다.",
                business_hours="평일 09:00-18:00, 토요일 09:00-13:00",
                is_verified=random.choice([True, False])
            )
            clinics.append(clinic)
        
        Clinic.objects.bulk_create(clinics)
        print(f"✅ {count}개 치과 생성 완료")
        return Clinic.objects.all()

    def create_reviews_and_analysis(self, clinics):
        """리뷰 및 감성 분석 데이터 생성"""
        print("📝 리뷰 및 감성 분석 데이터 생성 중...")
        
        # 기존 데이터 삭제
        Review.objects.all().delete()
        SentimentAnalysis.objects.all().delete()
        PriceData.objects.all().delete()
        
        total_reviews = 0
        
        for clinic in clinics:
            # 치과별 리뷰 수 (5~80개, 가중치 적용)
            review_count = random.choices(
                [random.randint(5, 15), random.randint(15, 30), random.randint(30, 50), random.randint(50, 80)],
                weights=[40, 35, 20, 5]
            )[0]
            
            reviews = []
            sentiment_analyses = []
            price_data = []
            
            for _ in range(review_count):
                # 긍정/부정 리뷰 비율 (75% 긍정)
                is_positive = random.random() < 0.75
                
                if is_positive:
                    review_text = random.choice(self.positive_reviews)
                    base_scores = {
                        'price': random.uniform(0.2, 1.0),
                        'skill': random.uniform(0.3, 1.0),
                        'kindness': random.uniform(0.2, 1.0),
                        'waiting_time': random.uniform(0.1, 0.8),
                        'facility': random.uniform(0.2, 0.9),
                        'overtreatment': random.uniform(0.3, 1.0),
                    }
                    rating = random.choices([3, 4, 5], weights=[10, 40, 50])[0]
                else:
                    review_text = random.choice(self.negative_reviews)
                    base_scores = {
                        'price': random.uniform(-1.0, -0.1),
                        'skill': random.uniform(-0.8, 0.1),
                        'kindness': random.uniform(-1.0, -0.1),
                        'waiting_time': random.uniform(-1.0, -0.2),
                        'facility': random.uniform(-0.9, 0.0),
                        'overtreatment': random.uniform(-1.0, -0.2),
                    }
                    rating = random.choices([1, 2, 3], weights=[30, 50, 20])[0]
                
                # 가격 정보가 포함된 리뷰인 경우
                treatment_type = None
                price = None
                if '{price}' in review_text and random.random() < 0.4:
                    # 치과의 전문분야 중에서 선택
                    clinic_treatments = [t.strip() for t in clinic.specialties.split(',')]
                    available_treatments = [t for t in clinic_treatments if t in self.price_ranges]
                    
                    if available_treatments:
                        treatment_type = random.choice(available_treatments)
                        price_range = self.price_ranges[treatment_type]
                        price = random.randint(price_range[0], price_range[1])
                        review_text = review_text.format(price=price)
                    else:
                        review_text = review_text.replace('{price}만원으로 ', '').replace('{price}만원이나 ', '비싸게 ')
                else:
                    review_text = review_text.replace('{price}만원으로 ', '').replace('{price}만원이나 ', '비싸게 ')
                
                # 리뷰 생성
                review_date = timezone.now() - timedelta(days=random.randint(1, 730))  # 2년 범위
                external_id = f"{clinic.id}_{random.randint(100000, 999999)}_{len(reviews)}"
                review = Review(
                    clinic=clinic,
                    source=random.choice(['naver', 'google']),
                    original_text=review_text,
                    processed_text=review_text,
                    original_rating=rating,
                    review_date=review_date,
                    reviewer_hash=f"user_{random.randint(10000, 99999)}",
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
                    model_version='unified_v1.0',
                    confidence_score=Decimal(str(round(random.uniform(0.75, 0.98), 2)))
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
                        extraction_confidence=Decimal(str(round(random.uniform(0.85, 0.98), 2))),
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
        
        print(f"✅ 총 {total_reviews}개 리뷰 및 분석 데이터 생성 완료")

    def create_sample_recommendations(self):
        """샘플 추천 로그 생성"""
        print("🎯 샘플 추천 로그 생성 중...")
        
        from apps.recommendations.models import RecommendationLog
        
        # 기존 로그 삭제
        RecommendationLog.objects.all().delete()
        
        users = list(User.objects.filter(is_superuser=False))
        
        for _ in range(100):  # 100개 추천 로그
            user = random.choice(users) if users else None
            district = random.choice(self.districts)
            treatment_type = random.choice(self.treatment_types) if random.random() < 0.6 else None
            
            # 해당 지역 치과들 중 상위 10개 선택
            clinics = list(Clinic.objects.filter(district=district).order_by('-total_reviews')[:10])
            recommended_clinic_ids = [clinic.id for clinic in clinics]
            
            RecommendationLog.objects.create(
                user=user,
                district=district,
                treatment_type=treatment_type,
                recommended_clinics=recommended_clinic_ids,
                algorithm_version='unified_v1.0'
            )
        
        print("✅ 샘플 추천 로그 생성 완료")

    def run(self):
        """전체 통합 데이터 생성 실행"""
        print("🚀 통합 더미 데이터 생성 시작...")
        print("=" * 60)
        
        # 1. 사용자 계정 생성
        self.create_admin_user()
        self.create_test_users()
        
        # 2. 치과 데이터 생성 (200개)
        clinics = self.create_clinics(200)
        
        # 3. 리뷰 및 분석 데이터 생성
        self.create_reviews_and_analysis(clinics)
        
        # 4. 추천 로그 생성
        self.create_sample_recommendations()
        
        print("=" * 60)
        print("✅ 통합 더미 데이터 생성 완료!")
        print(f"📊 생성된 데이터:")
        print(f"   - 치과: {Clinic.objects.count()}개")
        print(f"   - 리뷰: {Review.objects.count()}개")
        print(f"   - 감성분석: {SentimentAnalysis.objects.count()}개")
        print(f"   - 가격데이터: {PriceData.objects.count()}개")
        print(f"   - 사용자: {User.objects.count()}명")
        print(f"   - 지역: {len(self.districts)}개 자치구")
        print(f"   - 치료종류: {len(self.treatment_types)}개")
        print("=" * 60)
        print("🔑 관리자 계정: admin@dental.com / admin123!@#")
        print("🔑 테스트 계정: user1@test.com / test123!@#")
        print("=" * 60)
        
        # 지역별 통계 출력
        print("📍 지역별 치과 분포:")
        for district in self.districts:
            count = Clinic.objects.filter(district=district).count()
            print(f"   - {district}: {count}개")

if __name__ == '__main__':
    creator = UnifiedDataCreator()
    creator.run()