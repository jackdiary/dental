"""
리뷰 앱 URL 설정
"""
from django.urls import path
from . import api_views

app_name = 'reviews'

urlpatterns = [
    # 크롤링 관련 API
    path('crawl/', api_views.trigger_crawling, name='trigger_crawling'),
    path('status/<int:clinic_id>/', api_views.crawling_status, name='crawling_status'),
    
    # 리뷰 관련 API
    path('clinic/<int:clinic_id>/', api_views.clinic_reviews, name='clinic_reviews'),
    path('statistics/<int:clinic_id>/', api_views.review_statistics, name='review_statistics'),
    
    # 리뷰 관리 API
    path('mark-processed/', api_views.mark_reviews_processed, name='mark_reviews_processed'),
    path('flag/', api_views.flag_reviews, name='flag_reviews'),
    
    # 테스트용 API
    path('test/', api_views.CrawlingTestView.as_view(), name='crawling_test'),
]