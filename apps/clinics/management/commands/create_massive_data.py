"""
Django 관리 명령어로 대량 데이터 생성
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from decimal import Decimal
import random
from datetime import timedelta

from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData


class Command(BaseCommand):
    help = '대량의 치과 및 리뷰 데이터를 생성합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clinics',
            type=int,
            default=100,
            help='생성할 치과 수 (기본값: 100)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='기존 데이터를 모두 삭제하고 새로 생성'
        )

    def handle(self, *args, **options):
        self.stdout.write("🚀 대량 치과 데이터 생성 시작...")
        
        if options['clear']:
            self.stdout.write("🗑️ 기존 데이터 삭제 중...")
            PriceData.objects.all().delete()
            SentimentAnalysis.objects.all().delete()
            Review.objects.all().delete()
            Clinic.objects.all().delete()
            self.stdout.write("✅ 기존 데이터 삭제 완료")

        # 실제 치과 데이터 생성
        self.create_real_clinics()
        
        # 추가 치과 데이터 생성
        clinic_count = options['clinics']
        self.create_additional_clinics(clinic_count)
        
        # 리뷰 및 분석 데이터 생성
        self.create_reviews_and_analysis()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"✅ 데이터 생성 완료!\n"
                f"   - 치과: {Clinic.objects.count()}개\n"
                f"   - 리뷰: {Review.objects.count()}개\n"
                f"   - 감성분석: {SentimentAnalysis.objects.count()}개\n"
                f"   - 가격데이터: {PriceData.objects.count()}개"
            )
        )

    def create_real_clinics(self):
        """실제 치과 정보 생성"""
        self.stdout.write("🏥 실제 치과 정보 생성 중...")
        
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
            }
        ]
        
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
                self.stdout.write(f"✅ {clinic.name} 생성")

    def create_additional_clinics(self, count):
        """추가 치과 데이터 생성"""
        self.stdout.write(f"🏥 {count}개 추가 치과 생성 중...")
        
        districts = [
            '강남구', '강동구', '강북구', '강서구', '관악구',
            '광진구', '구로구', '금천구', '노원구', '도봉구',
            '동대문구', '동작구', '마포구', '서대문구', '서초구',
            '성동구', '성북구', '송파구', '양천구', '영등포구',
            '용산구', '은평구', '종로구', '중구', '중랑구'
        ]
        
        clinic_names = [
            '미소치과', '행복치과', '건강치과', '밝은치과', '새로운치과',
            '든든치과', '믿음치과', '정성치과', '친절치과', '전문치과'
        ]
        
        treatments = [
            '스케일링', '임플란트', '교정', '미백', '신경치료', '발치',
            '충치치료', '크라운', '브릿지', '틀니'
        ]
        
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
        
        self.stdout.write(f"✅ {count}개 치과 생성 완료")

    def create_reviews_and_analysis(self):
        """리뷰 및 감성분석 데이터 생성"""
        self.stdout.write("📝 리뷰 및 감성분석 데이터 생성 중...")
        
        positive_reviews = [
            "의사선생님이 정말 친절하시고 설명도 자세히 해주셔서 좋았어요.",
            "스케일링 받았는데 전혀 아프지 않게 해주셨어요.",
            "임플란트 상담받았는데 가격도 합리적이고 설명이 자세해서 신뢰가 갔어요.",
            "교정 상담 받았는데 과잉진료 없이 정직하게 상담해주셔서 좋았습니다.",
            "신경치료 받았는데 아프지 않게 잘해주셨어요."
        ]
        
        negative_reviews = [
            "가격이 너무 비싸요. 다른 곳보다 훨씬 비싸면서 서비스는 별로였어요.",
            "대기시간이 너무 길어서 힘들었어요.",
            "과잉진료 의심스러워요. 꼭 필요하지 않은 치료까지 권하시는 것 같아요.",
            "직원분들이 불친절해요.",
            "시설이 좀 오래된 것 같아요."
        ]
        
        clinics = Clinic.objects.all()
        total_reviews = 0
        
        for clinic in clinics:
            review_count = random.randint(10, 50)
            
            for _ in range(review_count):
                is_positive = random.random() < 0.7
                
                if is_positive:
                    review_text = random.choice(positive_reviews)
                    rating = random.choices([3, 4, 5], weights=[10, 40, 50])[0]
                    base_scores = {
                        'price': random.uniform(0.2, 1.0),
                        'skill': random.uniform(0.3, 1.0),
                        'kindness': random.uniform(0.2, 1.0),
                        'waiting_time': random.uniform(0.1, 0.8),
                        'facility': random.uniform(0.2, 0.9),
                        'overtreatment': random.uniform(0.3, 1.0),
                    }
                else:
                    review_text = random.choice(negative_reviews)
                    rating = random.choices([1, 2, 3], weights=[30, 50, 20])[0]
                    base_scores = {
                        'price': random.uniform(-1.0, -0.1),
                        'skill': random.uniform(-0.8, 0.1),
                        'kindness': random.uniform(-1.0, -0.1),
                        'waiting_time': random.uniform(-1.0, -0.2),
                        'facility': random.uniform(-0.9, 0.0),
                        'overtreatment': random.uniform(-1.0, -0.2),
                    }
                
                review_date = timezone.now() - timedelta(days=random.randint(1, 365))
                
                review = Review.objects.create(
                    clinic=clinic,
                    source=random.choice(['naver', 'google']),
                    original_text=review_text,
                    processed_text=review_text,
                    original_rating=rating,
                    review_date=review_date,
                    reviewer_hash=f"user_{random.randint(10000, 99999)}",
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
                    model_version='command_v1.0',
                    confidence_score=Decimal(str(round(random.uniform(0.75, 0.98), 2)))
                )
                
                total_reviews += 1
            
            # 치과 통계 업데이트
            reviews = Review.objects.filter(clinic=clinic)
            clinic.total_reviews = reviews.count()
            clinic.average_rating = Decimal(str(round(
                sum(r.original_rating for r in reviews) / reviews.count(), 2
            )))
            clinic.save()
        
        self.stdout.write(f"✅ {total_reviews}개 리뷰 및 분석 데이터 생성 완료")