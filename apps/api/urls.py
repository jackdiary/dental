"""
API URL Configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import health_check, cors_health_check
from .price_views import price_comparison, regional_price_stats, treatment_types
from .analysis_views import clinic_analysis, clinic_reviews_with_analysis, district_analysis_summary
from apps.clinics.views import clinic_search

# Import views when they are created
# from .views import (
#     RecommendationViewSet,
#     ClinicViewSet,
#     PriceComparisonViewSet,
# )

router = DefaultRouter()
# Register viewsets when they are created
# router.register(r'clinics', ClinicViewSet)
# router.register(r'recommendations', RecommendationViewSet)
# router.register(r'prices', PriceComparisonViewSet)

app_name = 'api'

urlpatterns = [
    # Health check
    path('health/', health_check, name='health_check'),
    path('health/cors/', cors_health_check, name='cors_health_check'),
    
    # Authentication endpoints
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/', include('apps.accounts.urls')),
    
    # API endpoints
    path('', include(router.urls)),
    
    # Clinics API
    path('clinics/', include('apps.clinics.urls')),
    path('clinics/search/', clinic_search, name='clinic_search'),
    
    # Reviews API
    path('reviews/', include('apps.reviews.urls')),
    
    # Recommendations API
    path('', include('apps.recommendations.urls')),
    
    # Price Comparison API
    path('price-comparison/', price_comparison, name='price_comparison'),
    path('price-stats/', regional_price_stats, name='regional_price_stats'),
    path('treatment-types/', treatment_types, name='treatment_types'),
    
    # Analysis API
    path('clinics/<int:clinic_id>/analysis/', clinic_analysis, name='clinic_analysis'),
    path('clinics/<int:clinic_id>/reviews/', clinic_reviews_with_analysis, name='clinic_reviews_analysis'),
    path('district-analysis/', district_analysis_summary, name='district_analysis_summary'),
]

from django.conf import settings

if settings.DEBUG:
    # Swagger/OpenAPI 문서화
    from rest_framework import permissions
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi

    schema_view = get_schema_view(
        openapi.Info(
            title="치과 추천 AI API",
            default_version='v1',
            description="""
            치과 추천 AI 시스템 API 문서
            
            ## 주요 기능
            - 지역 기반 치과 추천
            - 리뷰 감성 분석
            - 가격 비교
            - 치과 상세 정보 조회
            
            ## 인증
            JWT 토큰 기반 인증을 사용합니다.
            """,
            terms_of_service="https://www.example.com/policies/terms/",
            contact=openapi.Contact(email="contact@dentalai.com"),
            license=openapi.License(name="MIT License"),
        ),
        public=True,
        permission_classes=[permissions.AllowAny],
    )

    # Swagger URL 패턴 추가
    urlpatterns += [
        path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
        path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]