"""
추천 시스템 URL 설정
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'recommendations'

# API URL 패턴
urlpatterns = [
    # 추천 API
    path('recommend/', views.RecommendationAPIView.as_view(), name='recommend'),
    
    # 치과 상세 정보
    path('clinics/<int:clinic_id>/', views.ClinicDetailAPIView.as_view(), name='clinic-detail'),
    
    # 가격 비교
    path('prices/compare/', views.PriceComparisonAPIView.as_view(), name='price-compare'),
    
    # 추천 피드백
    path('feedback/', views.RecommendationFeedbackAPIView.as_view(), name='feedback'),
    
    # 관리자 API
    path('admin/crawl/', views.trigger_crawling, name='trigger-crawling'),
    path('admin/crawl/<str:task_id>/status/', views.crawling_status, name='crawling-status'),
    
    # 모니터링 API
    path('admin/system/status/', views.system_status, name='system-status'),
    path('admin/ml/metrics/', views.ml_model_metrics, name='ml-metrics'),
]