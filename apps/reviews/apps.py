from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reviews'
    
    def ready(self):
        """앱 초기화 시 크롤러 등록"""
        try:
            from .crawlers.naver import register_naver_crawler
            from .crawlers.google import register_google_crawler
            
            register_naver_crawler()
            register_google_crawler()
        except Exception as e:
            # 개발 환경에서는 크롤러 등록 실패를 무시
            pass
    verbose_name = '리뷰 관리'