"""
리뷰 분석 API 뷰
"""
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count, Q
from collections import Counter
import re

from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis


@api_view(['GET'])
def clinic_analysis(request, clinic_id):
    """
    특정 치과의 리뷰 분석 결과 API
    """
    try:
        clinic = Clinic.objects.get(id=clinic_id)
    except Clinic.DoesNotExist:
        return Response({
            'error': '치과를 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # 리뷰 통계
        reviews = Review.objects.filter(clinic=clinic, is_processed=True)
        total_reviews = reviews.count()
        
        if total_reviews == 0:
            return Response({
                'clinic_id': clinic_id,
                'clinic_name': clinic.name,
                'total_reviews': 0,
                'message': '분석할 리뷰가 없습니다.'
            })
        
        # 평균 평점
        avg_rating = reviews.aggregate(avg=Avg('original_rating'))['avg']
        
        # 긍정 리뷰 비율 (4점 이상)
        positive_reviews = reviews.filter(original_rating__gte=4).count()
        positive_ratio = round((positive_reviews / total_reviews) * 100, 1)
        
        # 감성 분석 데이터
        sentiment_analyses = SentimentAnalysis.objects.filter(
            review__clinic=clinic
        )
        
        if sentiment_analyses.exists():
            # 측면별 평균 점수
            aspect_scores = sentiment_analyses.aggregate(
                price=Avg('price_score'),
                skill=Avg('skill_score'),
                kindness=Avg('kindness_score'),
                waiting_time=Avg('waiting_time_score'),
                facility=Avg('facility_score'),
                overtreatment=Avg('overtreatment_score')
            )
            
            # 신뢰도 평균
            avg_confidence = sentiment_analyses.aggregate(
                confidence=Avg('confidence_score')
            )['confidence']
            
            confidence = round(float(avg_confidence) * 100, 1) if avg_confidence else 0
        else:
            aspect_scores = {
                'price': 0,
                'skill': 0,
                'kindness': 0,
                'waiting_time': 0,
                'facility': 0,
                'overtreatment': 0
            }
            confidence = 0
        
        # 키워드 추출
        top_keywords = extract_top_keywords(reviews)
        
        return Response({
            'clinic_id': clinic_id,
            'clinic_name': clinic.name,
            'total_reviews': total_reviews,
            'average_rating': round(float(avg_rating), 1) if avg_rating else 0,
            'positive_ratio': positive_ratio,
            'confidence': confidence,
            'aspect_scores': {
                'price': round(float(aspect_scores['price']), 2) if aspect_scores['price'] else 0,
                'skill': round(float(aspect_scores['skill']), 2) if aspect_scores['skill'] else 0,
                'kindness': round(float(aspect_scores['kindness']), 2) if aspect_scores['kindness'] else 0,
                'waiting_time': round(float(aspect_scores['waiting_time']), 2) if aspect_scores['waiting_time'] else 0,
                'facility': round(float(aspect_scores['facility']), 2) if aspect_scores['facility'] else 0,
                'overtreatment': round(float(aspect_scores['overtreatment']), 2) if aspect_scores['overtreatment'] else 0,
            },
            'top_keywords': top_keywords
        })
        
    except Exception as e:
        return Response({
            'error': f'리뷰 분석 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def clinic_reviews_with_analysis(request, clinic_id):
    """
    치과 리뷰 목록 (감성 분석 포함) API
    """
    try:
        clinic = Clinic.objects.get(id=clinic_id)
    except Clinic.DoesNotExist:
        return Response({
            'error': '치과를 찾을 수 없습니다.'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        # 페이지네이션 파라미터
        page = int(request.GET.get('page', 1))
        page_size = int(request.GET.get('page_size', 10))
        offset = (page - 1) * page_size
        
        # 리뷰 조회 (최신순)
        reviews = Review.objects.filter(
            clinic=clinic, 
            is_processed=True
        ).select_related('sentimentanalysis').order_by('-review_date')[offset:offset + page_size]
        
        total_count = Review.objects.filter(clinic=clinic, is_processed=True).count()
        
        results = []
        for review in reviews:
            review_data = {
                'id': review.id,
                'original_text': review.original_text,
                'original_rating': review.original_rating,
                'review_date': review.review_date.isoformat(),
                'source': review.source,
                'sentiment_analysis': None
            }
            
            # 감성 분석 데이터 추가
            try:
                sentiment = review.sentimentanalysis
                review_data['sentiment_analysis'] = {
                    'price': float(sentiment.price_score),
                    'skill': float(sentiment.skill_score),
                    'kindness': float(sentiment.kindness_score),
                    'waiting_time': float(sentiment.waiting_time_score),
                    'facility': float(sentiment.facility_score),
                    'overtreatment': float(sentiment.overtreatment_score),
                    'confidence': float(sentiment.confidence_score)
                }
            except SentimentAnalysis.DoesNotExist:
                pass
            
            results.append(review_data)
        
        return Response({
            'results': results,
            'count': total_count,
            'page': page,
            'page_size': page_size,
            'total_pages': (total_count + page_size - 1) // page_size
        })
        
    except Exception as e:
        return Response({
            'error': f'리뷰 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def extract_top_keywords(reviews):
    """
    리뷰에서 상위 키워드 추출
    """
    # 치과 관련 키워드 사전
    dental_keywords = {
        'price': ['가격', '비용', '돈', '비싸', '싸', '저렴', '합리적', '바가지', '할인'],
        'skill': ['실력', '숙련', '경험', '전문', '정확', '꼼꼼', '대충', '미숙', '능숙'],
        'kindness': ['친절', '불친절', '상냥', '무뚝뚝', '따뜻', '차갑', '예의', '무례'],
        'waiting_time': ['대기', '기다림', '빠르', '느리', '신속', '지연', '늦', '정시'],
        'facility': ['시설', '장비', '깨끗', '더럽', '위생', '소독', '최신', '낡'],
        'overtreatment': ['과잉진료', '과잉', '불필요', '억지', '강요', '적절', '필요']
    }
    
    # 모든 리뷰 텍스트 합치기
    all_text = ' '.join([review.original_text for review in reviews])
    
    # 카테고리별 키워드 카운트
    category_keywords = {}
    
    for category, keywords in dental_keywords.items():
        keyword_counts = []
        
        for keyword in keywords:
            count = len(re.findall(keyword, all_text))
            if count > 0:
                keyword_counts.append((keyword, count))
        
        # 상위 3개 키워드만 선택
        keyword_counts.sort(key=lambda x: x[1], reverse=True)
        category_keywords[category] = [kw for kw, count in keyword_counts[:3]]
    
    return category_keywords


@api_view(['GET'])
def district_analysis_summary(request):
    """
    지역별 분석 요약 API
    """
    district = request.GET.get('district')
    
    try:
        queryset = Clinic.objects.all()
        
        if district:
            queryset = queryset.filter(district__icontains=district)
        
        # 지역별 통계
        clinics = queryset.annotate(
            review_count=Count('review', filter=Q(review__is_processed=True)),
            avg_rating=Avg('review__original_rating', filter=Q(review__is_processed=True))
        ).filter(review_count__gt=0)
        
        summary = {
            'total_clinics': clinics.count(),
            'total_reviews': sum([clinic.review_count for clinic in clinics]),
            'avg_rating': round(sum([clinic.avg_rating or 0 for clinic in clinics]) / max(clinics.count(), 1), 1),
            'top_clinics': []
        }
        
        # 상위 치과 (리뷰 수 기준)
        top_clinics = clinics.order_by('-review_count')[:5]
        
        for clinic in top_clinics:
            summary['top_clinics'].append({
                'id': clinic.id,
                'name': clinic.name,
                'district': clinic.district,
                'review_count': clinic.review_count,
                'avg_rating': round(float(clinic.avg_rating), 1) if clinic.avg_rating else 0
            })
        
        return Response(summary)
        
    except Exception as e:
        return Response({
            'error': f'지역별 분석 요약 조회 중 오류가 발생했습니다: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)