"""
CORS 설정 유틸리티 모듈
환경별 CORS 설정 관리 및 검증 기능 제공
"""

import os
import logging
from typing import List, Dict, Any, Optional
from django.conf import settings

logger = logging.getLogger(__name__)


class EnvironmentDetector:
    """현재 실행 환경을 감지하는 클래스"""
    
    @staticmethod
    def is_production() -> bool:
        """프로덕션 환경인지 확인"""
        environment = os.getenv('ENVIRONMENT', '').lower()
        debug = os.getenv('DEBUG', 'True').lower()
        
        # 환경 변수 또는 DEBUG 설정으로 판단
        return environment == 'production' or debug == 'false'
    
    @staticmethod
    def is_development() -> bool:
        """개발 환경인지 확인"""
        return not EnvironmentDetector.is_production()
    
    @staticmethod
    def get_current_domain() -> str:
        """현재 도메인을 반환"""
        if EnvironmentDetector.is_production():
            return os.getenv('BACKEND_DOMAIN', 'https://backend.run.app')
        return 'http://localhost:8000'
    
    @staticmethod
    def get_environment_name() -> str:
        """환경 이름을 반환"""
        return 'production' if EnvironmentDetector.is_production() else 'development'


class CORSConfigManager:
    """CORS 설정을 관리하는 클래스"""
    
    # 환경별 기본 CORS 설정
    DEFAULT_CORS_SETTINGS = {
        'development': {
            'allowed_origins': [
                'http://localhost:3000',
                'http://127.0.0.1:3000',
                'http://localhost:3001',
                'http://127.0.0.1:3001',
                'http://localhost:5173',  # Vite 기본 포트
                'http://127.0.0.1:5173',
            ],
            'allow_all_origins': True,  # 개발 환경에서는 편의를 위해 허용
            'allow_credentials': True,
            'allow_headers': [
                'accept',
                'accept-encoding',
                'authorization',
                'content-type',
                'dnt',
                'origin',
                'user-agent',
                'x-csrftoken',
                'x-requested-with',
            ],
            'allow_methods': [
                'DELETE',
                'GET',
                'OPTIONS',
                'PATCH',
                'POST',
                'PUT',
            ],
        },
        'production': {
            'allowed_origins': [
                'https://dental-ai-frontend-602563947939.asia-northeast3.run.app',
            ],
            'allow_all_origins': False,  # 프로덕션에서는 보안을 위해 비허용
            'allow_credentials': True,
            'allow_headers': [
                'accept',
                'accept-encoding',
                'authorization',
                'content-type',
                'origin',
                'user-agent',
                'x-csrftoken',
                'x-requested-with',
            ],
            'allow_methods': [
                'DELETE',
                'GET',
                'OPTIONS',
                'PATCH',
                'POST',
                'PUT',
            ],
        }
    }
    
    def __init__(self):
        self.environment = EnvironmentDetector.get_environment_name()
        self._cached_settings = None
    
    def get_allowed_origins(self) -> List[str]:
        """허용된 오리진 목록을 반환"""
        base_origins = self.DEFAULT_CORS_SETTINGS[self.environment]['allowed_origins'].copy()
        
        # 환경 변수에서 추가 오리진 로드
        env_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
        if env_origins:
            additional_origins = [origin.strip() for origin in env_origins.split(',') if origin.strip()]
            base_origins.extend(additional_origins)
        
        # 중복 제거
        return list(set(base_origins))
    
    def get_cors_settings(self) -> Dict[str, Any]:
        """현재 환경에 맞는 CORS 설정을 반환"""
        if self._cached_settings is not None:
            return self._cached_settings
        
        base_settings = self.DEFAULT_CORS_SETTINGS[self.environment].copy()
        
        # 환경 변수로 오버라이드
        cors_settings = {
            'CORS_ALLOWED_ORIGINS': self.get_allowed_origins(),
            'CORS_ALLOW_ALL_ORIGINS': self._get_bool_env('CORS_ALLOW_ALL_ORIGINS', base_settings['allow_all_origins']),
            'CORS_ALLOW_CREDENTIALS': self._get_bool_env('CORS_ALLOW_CREDENTIALS', base_settings['allow_credentials']),
            'CORS_ALLOW_HEADERS': base_settings['allow_headers'],
            'CORS_ALLOW_METHODS': base_settings['allow_methods'],
        }
        
        # 프로덕션 환경에서는 CORS_ALLOW_ALL_ORIGINS를 False로 강제
        if self.environment == 'production' and cors_settings['CORS_ALLOW_ALL_ORIGINS']:
            logger.warning("프로덕션 환경에서 CORS_ALLOW_ALL_ORIGINS=True는 보안상 권장되지 않습니다.")
            if not cors_settings['CORS_ALLOWED_ORIGINS']:
                logger.error("프로덕션 환경에서 CORS_ALLOWED_ORIGINS가 비어있습니다!")
        
        self._cached_settings = cors_settings
        return cors_settings
    
    def get_csrf_trusted_origins(self) -> List[str]:
        """CSRF 신뢰할 수 있는 오리진 목록을 CORS 설정과 일치하도록 반환"""
        cors_origins = self.get_allowed_origins()
        
        # 기본 신뢰할 수 있는 오리진
        base_trusted_origins = []
        if self.environment == 'production':
            base_trusted_origins = [
                'https://*.run.app',
                'https://*.googleapis.com',
            ]
        
        # CORS 허용 오리진을 CSRF 신뢰 오리진에 추가
        trusted_origins = base_trusted_origins + cors_origins
        
        # 환경 변수에서 추가 신뢰 오리진 로드
        env_trusted_origins = os.getenv('CSRF_TRUSTED_ORIGINS', '')
        if env_trusted_origins:
            additional_trusted = [origin.strip() for origin in env_trusted_origins.split(',') if origin.strip()]
            trusted_origins.extend(additional_trusted)
        
        # 중복 제거
        return list(set(trusted_origins))
    
    def get_security_settings(self) -> Dict[str, Any]:
        """CORS와 함께 적용할 보안 설정을 반환"""
        cors_settings = self.get_cors_settings()
        
        security_settings = {
            **cors_settings,
            'CSRF_TRUSTED_ORIGINS': self.get_csrf_trusted_origins(),
        }
        
        # 프로덕션 환경에서 추가 보안 설정
        if self.environment == 'production':
            security_settings.update({
                'SECURE_CONTENT_TYPE_NOSNIFF': True,
                'SECURE_BROWSER_XSS_FILTER': True,
                'SECURE_REFERRER_POLICY': 'strict-origin-when-cross-origin',
                'X_FRAME_OPTIONS': 'DENY',
                'CSRF_COOKIE_SECURE': True,
                'CSRF_COOKIE_HTTPONLY': True,
                'CSRF_COOKIE_SAMESITE': 'Lax',
            })
        
        return security_settings
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """환경 변수에서 boolean 값을 안전하게 가져옴"""
        value = os.getenv(key, str(default)).lower()
        return value in ('true', '1', 'yes', 'on')
    
    def validate_cors_settings(self) -> List[str]:
        """CORS 설정의 유효성을 검증하고 오류 목록을 반환"""
        errors = []
        settings_dict = self.get_cors_settings()
        
        # 1. CORS_ALLOW_ALL_ORIGINS와 CORS_ALLOWED_ORIGINS 충돌 검사
        if settings_dict['CORS_ALLOW_ALL_ORIGINS'] and settings_dict['CORS_ALLOWED_ORIGINS']:
            if self.environment == 'production':
                errors.append("프로덕션 환경에서 CORS_ALLOW_ALL_ORIGINS=True와 CORS_ALLOWED_ORIGINS를 동시에 설정할 수 없습니다")
        
        # 2. 프로덕션 환경에서 CORS_ALLOW_ALL_ORIGINS=True 검사
        if self.environment == 'production' and settings_dict['CORS_ALLOW_ALL_ORIGINS']:
            errors.append("프로덕션 환경에서 CORS_ALLOW_ALL_ORIGINS=True는 보안상 위험합니다")
        
        # 3. 오리진 패턴 검증
        for origin in settings_dict['CORS_ALLOWED_ORIGINS']:
            if not self._is_valid_origin(origin):
                errors.append(f"잘못된 오리진 패턴: {origin}")
        
        # 4. 프로덕션에서 허용된 오리진이 없는 경우
        if (self.environment == 'production' and 
            not settings_dict['CORS_ALLOW_ALL_ORIGINS'] and 
            not settings_dict['CORS_ALLOWED_ORIGINS']):
            errors.append("프로덕션 환경에서 허용된 오리진이 설정되지 않았습니다")
        
        return errors
    
    def _is_valid_origin(self, origin: str) -> bool:
        """오리진 패턴이 유효한지 검사"""
        if not origin:
            return False
        
        # 기본적인 URL 형식 검사
        if not (origin.startswith('http://') or origin.startswith('https://')):
            return False
        
        # django-cors-headers는 와일드카드 패턴을 지원하지 않음
        if '*' in origin and not origin.startswith('https://'):
            return False
        
        return True
    
    def log_cors_configuration(self) -> None:
        """현재 CORS 설정을 로그에 출력"""
        settings_dict = self.get_cors_settings()
        
        logger.info(f"=== CORS 설정 정보 (환경: {self.environment}) ===")
        logger.info(f"CORS_ALLOW_ALL_ORIGINS: {settings_dict['CORS_ALLOW_ALL_ORIGINS']}")
        logger.info(f"CORS_ALLOW_CREDENTIALS: {settings_dict['CORS_ALLOW_CREDENTIALS']}")
        
        if settings_dict['CORS_ALLOWED_ORIGINS']:
            logger.info("허용된 오리진:")
            for origin in settings_dict['CORS_ALLOWED_ORIGINS']:
                logger.info(f"  - {origin}")
        else:
            logger.info("허용된 오리진: 없음")
        
        # 검증 결과도 로그에 출력
        errors = self.validate_cors_settings()
        if errors:
            logger.warning("CORS 설정 검증 오류:")
            for error in errors:
                logger.warning(f"  - {error}")
        else:
            logger.info("✅ CORS 설정 검증 완료")


class CORSDebugger:
    """CORS 관련 디버깅 유틸리티"""
    
    @staticmethod
    def log_cors_request(request, response=None) -> None:
        """CORS 요청을 로깅"""
        origin = request.META.get('HTTP_ORIGIN')
        method = request.method
        
        if origin:
            logger.debug(f"CORS 요청: {method} {request.path} from {origin}")
            
            if response:
                cors_headers = {
                    key: value for key, value in response.items() 
                    if key.lower().startswith('access-control-')
                }
                if cors_headers:
                    logger.debug(f"CORS 응답 헤더: {cors_headers}")
    
    @staticmethod
    def validate_cors_headers(response) -> Dict[str, Any]:
        """응답의 CORS 헤더를 검증"""
        cors_headers = {}
        
        for key, value in response.items():
            if key.lower().startswith('access-control-'):
                cors_headers[key] = value
        
        return {
            'has_cors_headers': bool(cors_headers),
            'cors_headers': cors_headers,
            'allow_origin': response.get('Access-Control-Allow-Origin'),
            'allow_credentials': response.get('Access-Control-Allow-Credentials'),
            'allow_methods': response.get('Access-Control-Allow-Methods'),
            'allow_headers': response.get('Access-Control-Allow-Headers'),
        }
    
    @staticmethod
    def create_health_check_data() -> Dict[str, Any]:
        """CORS 헬스 체크용 데이터 생성"""
        manager = CORSConfigManager()
        settings_dict = manager.get_cors_settings()
        errors = manager.validate_cors_settings()
        
        return {
            'environment': manager.environment,
            'cors_enabled': True,
            'cors_settings': {
                'allow_all_origins': settings_dict['CORS_ALLOW_ALL_ORIGINS'],
                'allowed_origins': settings_dict['CORS_ALLOWED_ORIGINS'],
                'allow_credentials': settings_dict['CORS_ALLOW_CREDENTIALS'],
                'allow_methods': settings_dict['CORS_ALLOW_METHODS'],
                'allow_headers': settings_dict['CORS_ALLOW_HEADERS'],
            },
            'validation_errors': errors,
            'is_valid': len(errors) == 0,
        }


# 전역 CORS 매니저 인스턴스
cors_manager = CORSConfigManager()


def get_cors_settings() -> Dict[str, Any]:
    """CORS 설정을 가져오는 편의 함수"""
    return cors_manager.get_cors_settings()


def get_security_settings() -> Dict[str, Any]:
    """CORS와 보안 설정을 함께 가져오는 편의 함수"""
    return cors_manager.get_security_settings()


def validate_and_log_cors() -> None:
    """CORS 설정을 검증하고 로깅하는 편의 함수"""
    cors_manager.log_cors_configuration()
    
    errors = cors_manager.validate_cors_settings()
    if errors:
        logger.error("CORS 설정에 문제가 있습니다:")
        for error in errors:
            logger.error(f"  - {error}")
        return False
    
    logger.info("✅ CORS 설정이 올바르게 구성되었습니다")
    return True