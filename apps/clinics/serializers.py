from rest_framework import serializers
from .models import Clinic


class ClinicListSerializer(serializers.ModelSerializer):
    """치과 목록용 시리얼라이저"""
    aspect_scores = serializers.SerializerMethodField()
    comprehensive_score = serializers.SerializerMethodField()
    price_info = serializers.SerializerMethodField()
    has_parking = serializers.BooleanField()
    night_service = serializers.BooleanField()
    weekend_service = serializers.BooleanField()
    
    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'address', 'district', 'phone', 
            'website', 'latitude', 'longitude', 'average_rating', 
            'total_reviews', 'is_verified', 'created_at',
            'has_parking', 'night_service', 'weekend_service', 
            'aspect_scores', 'comprehensive_score', 'price_info'
        ]

    def get_comprehensive_score(self, obj):
        """종합 점수 계산"""
        aspect_scores = self.get_aspect_scores(obj)
        if aspect_scores and aspect_scores.values():
            valid_scores = [s for s in aspect_scores.values() if s is not None]
            if valid_scores:
                return round(sum(valid_scores) / len(valid_scores), 2)
        return 3.5 # 기본값
    
    def get_aspect_scores(self, obj):
        """감성 분석 기반 측면별 점수"""
        try:
            from apps.analysis.models import SentimentAnalysis
            from django.db.models import Avg
            
            # 해당 치과의 모든 감성 분석 결과 평균 계산
            sentiment_avg = SentimentAnalysis.objects.filter(
                review__clinic=obj
            ).aggregate(
                price=Avg('price_score'),
                skill=Avg('skill_score'),
                kindness=Avg('kindness_score'),
                waiting=Avg('waiting_time_score'),
                facility=Avg('facility_score'),
                overtreatment=Avg('overtreatment_score')
            )
            
            # -1~1 범위를 1~5 범위로 변환
            aspect_scores = {}
            for key, value in sentiment_avg.items():
                if value is not None:
                    # -1~1을 1~5로 변환: (value + 1) * 2 + 1
                    aspect_scores[key] = round((float(value) + 1) * 2 + 1, 1)
                else:
                    aspect_scores[key] = 3.0  # 기본값
            
            return aspect_scores
        except Exception:
            # 기본값 반환
            return {
                'price': 3.5,
                'skill': 3.5,
                'kindness': 3.5,
                'waiting': 3.5,
                'facility': 3.5,
                'overtreatment': 3.5
            }

    def get_price_info(self, obj):
        """리스트용 요약 가격 정보 (치료별 평균)"""
        try:
            from apps.analysis.models import PriceData
            prices = PriceData.objects.filter(clinic=obj)
            summary = {}
            for price in prices:
                entry = summary.setdefault(price.treatment_type, {'total': 0, 'count': 0})
                entry['total'] += price.price
                entry['count'] += 1
                entry['currency'] = price.currency
            result = {}
            for treatment, data in summary.items():
                if data['count'] > 0:
                    result[treatment] = {
                        'average_price': int(data['total'] / data['count']),
                        'price_count': data['count'],
                        'currency': data.get('currency', 'KRW'),
                    }
            return result
        except Exception:
            return {}


class ClinicDetailSerializer(serializers.ModelSerializer):
    """치과 상세 정보용 시리얼라이저"""
    recent_reviews = serializers.SerializerMethodField()
    price_info = serializers.SerializerMethodField()
    aspect_scores = serializers.SerializerMethodField()
    comprehensive_score = serializers.SerializerMethodField()

    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'address', 'district', 'phone', 'website',
            'latitude', 'longitude', 'business_hours', 'description',
            'specialties', 'facilities', 'average_rating', 'total_reviews',
            'recent_reviews', 'price_info', 'is_verified', 'created_at', 'updated_at',
            'aspect_scores', 'comprehensive_score'
        ]

    def get_comprehensive_score(self, obj):
        """종합 점수 계산"""
        aspect_scores = self.get_aspect_scores(obj)
        if aspect_scores and aspect_scores.values():
            valid_scores = [s for s in aspect_scores.values() if s is not None]
            if valid_scores:
                return round(sum(valid_scores) / len(valid_scores), 2)
        return 3.5 # 기본값

    def get_aspect_scores(self, obj):
        """감성 분석 기반 측면별 점수"""
        try:
            from apps.analysis.models import SentimentAnalysis
            from django.db.models import Avg
            
            sentiment_avg = SentimentAnalysis.objects.filter(
                review__clinic=obj
            ).aggregate(
                price=Avg('price_score'),
                skill=Avg('skill_score'),
                kindness=Avg('kindness_score'),
                waiting=Avg('waiting_time_score'),
                facility=Avg('facility_score'),
                overtreatment=Avg('overtreatment_score')
            )
            
            aspect_scores = {}
            for key, value in sentiment_avg.items():
                if value is not None:
                    aspect_scores[key] = round((float(value) + 1) * 2 + 1, 1)
                else:
                    aspect_scores[key] = 3.0
            
            return aspect_scores
        except Exception:
            return {
                'price': 3.5,
                'skill': 3.5,
                'kindness': 3.5,
                'waiting': 3.5,
                'facility': 3.5,
                'overtreatment': 3.5
            }

    def get_recent_reviews(self, obj):
        """최근 리뷰 5개"""
        try:
            recent_reviews = obj.reviews.order_by('-created_at')[:5]
            return [
                {
                    'id': review.id,
                    'rating': review.original_rating,
                    'original_text': review.original_text[:100] + '...' if len(review.original_text) > 100 else review.original_text,
                    'source': review.source,
                    'created_at': review.created_at
                }
                for review in recent_reviews
            ]
        except Exception:
            return []
    
    def get_price_info(self, obj):
        """가격 정보"""
        try:
            from apps.analysis.models import PriceData
            price_data = {}
            prices = PriceData.objects.filter(clinic=obj)
            
            for price in prices:
                treatment = price.treatment_type
                if treatment not in price_data:
                    price_data[treatment] = []
                price_data[treatment].append({
                    'price': price.price,
                    'currency': price.currency,
                    'extraction_confidence': float(price.extraction_confidence)
                })
            
            # 치료별 평균 가격 계산
            avg_prices = {}
            for treatment, prices in price_data.items():
                if prices:
                    avg_price = sum(p['price'] for p in prices) / len(prices)
                    avg_prices[treatment] = {
                        'average_price': int(avg_price),
                        'price_count': len(prices),
                        'currency': prices[0]['currency']
                    }
            
            return avg_prices
        except Exception:
            return {}


class ClinicCreateSerializer(serializers.ModelSerializer):
    """치과 생성용 시리얼라이저"""
    
    class Meta:
        model = Clinic
        fields = [
            'name', 'address', 'district', 'phone', 'website',
            'latitude', 'longitude', 'business_hours', 'description',
            'specialties', 'facilities'
        ]
    
    def validate_phone(self, value):
        """전화번호 형식 검증"""
        import re
        if value and not re.match(r'^[\d\-\(\)\s]+$', value):
            raise serializers.ValidationError("올바른 전화번호 형식이 아닙니다.")
        return value
    
    def validate(self, attrs):
        """위도/경도 검증"""
        latitude = attrs.get('latitude')
        longitude = attrs.get('longitude')
        
        if latitude is not None and not (-90 <= latitude <= 90):
            raise serializers.ValidationError("위도는 -90도에서 90도 사이여야 합니다.")
        
        if longitude is not None and not (-180 <= longitude <= 180):
            raise serializers.ValidationError("경도는 -180도에서 180도 사이여야 합니다.")
        
        return attrs


class ClinicUpdateSerializer(serializers.ModelSerializer):
    """치과 수정용 시리얼라이저"""
    
    class Meta:
        model = Clinic
        fields = [
            'name', 'address', 'district', 'phone', 'website',
            'latitude', 'longitude', 'business_hours', 'description',
            'specialties', 'facilities'
        ]
    
    def validate_phone(self, value):
        """전화번호 형식 검증"""
        import re
        if value and not re.match(r'^[\d\-\(\)\s]+$', value):
            raise serializers.ValidationError("올바른 전화번호 형식이 아닙니다.")
        return value
