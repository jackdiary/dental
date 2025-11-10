"""
API 앱 설정
CORS 설정 검증 및 초기화 기능 포함
"""

from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api'
    verbose_name = 'API'
    
    def ready(self):
        """앱이 준비되었을 때 실행되는 초기화 코드"""
        # CORS 설정 검증
        self.validate_cors_configuration()
        
        # 시그널 등록 (필요시)
        # import apps.api.signals
    
    def validate_cors_configuration(self):
        """CORS 설정 유효성 검사"""
        try:
            from config.cors_settings import cors_manager, EnvironmentDetector
            
            logger.info("=== CORS 설정 검증 시작 ===")
            
            # 환경 정보 로깅
            environment = EnvironmentDetector.get_environment_name()
            logger.info(f"현재 환경: {environment}")
            
            # CORS 설정 검증
            errors = cors_manager.validate_cors_settings()
            
            if errors:
                logger.error("CORS 설정 검증 실패:")
                for error in errors:
                    logger.error(f"  - {error}")
                
                # 프로덕션 환경에서 심각한 오류가 있으면 경고
                if environment == 'production':
                    logger.critical("프로덕션 환경에서 CORS 설정 오류가 감지되었습니다!")
            else:
                logger.info("✅ CORS 설정 검증 완료 - 모든 설정이 올바릅니다")
            
            # CORS 설정 정보 로깅
            cors_manager.log_cors_configuration()
            
        except Exception as e:
            logger.error(f"CORS 설정 검증 중 오류 발생: {e}")
            
            # 개발 환경에서는 상세 오류 정보 출력
            if EnvironmentDetector.is_development():
                import traceback
                logger.debug(f"상세 오류 정보:\n{traceback.format_exc()}")