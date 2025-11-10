"""
Django 프로덕션 설정
Google Cloud Platform 배포용 설정
"""
import os
# import dj_database_url  # 사용하지 않음
from .base import *

# 기본 설정
DEBUG = False
ENVIRONMENT = 'production'

# Google Cloud 프로젝트 설정
GCP_PROJECT_ID = os.getenv('GCP_PROJECT_ID', 'dental-ai-2024')
GCP_REGION = os.getenv('GCP_REGION', 'asia-northeast3')

# 보안 설정
SECRET_KEY = os.getenv('SECRET_KEY', 'dental-ai-production-secret-key-2024-temp')
print(f"SECRET_KEY 설정됨: {SECRET_KEY[:10]}...")

# 허용된 호스트
ALLOWED_HOSTS = [
    '.run.app',  # Cloud Run 도메인
    '.googleapis.com',
    'localhost',
    '127.0.0.1',
]

# 환경 변수에서 추가 호스트 로드
additional_hosts = os.getenv('ALLOWED_HOSTS', '')
if additional_hosts:
    ALLOWED_HOSTS.extend([host.strip() for host in additional_hosts.split(',')])

# 데이터베이스 설정 (Cloud SQL PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dental_ai',
        'USER': 'dental_user',
        'PASSWORD': 'dental123!@#',
        'HOST': '/cloudsql/dental-ai-2024:asia-northeast3:dental-ai-db',
        'PORT': '',
    }
}

# 캐시 설정 (Redis 없이 더미 캐시 사용)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# 세션 설정 (데이터베이스 백엔드 사용)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 3600  # 1시간

# 정적 파일 설정 (Cloud Storage)
DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
STATICFILES_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'

GS_BUCKET_NAME = os.getenv('GS_BUCKET_NAME', f'{GCP_PROJECT_ID}-static')
GS_PROJECT_ID = GCP_PROJECT_ID
GS_DEFAULT_ACL = 'publicRead'
GS_FILE_OVERWRITE = False
GS_MAX_MEMORY_SIZE = 1024 * 1024 * 5  # 5MB

STATIC_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/static/'
MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/media/'

# 보안 설정 (HTTPS 리디렉션 비활성화)
SECURE_SSL_REDIRECT = False  # Cloud Run에서 HTTPS는 자동 처리됨
SECURE_HSTS_SECONDS = 0  # 비활성화
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

X_FRAME_OPTIONS = 'DENY'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
# CORS 및 보안 설정 (CORS 유틸리티 모듈 사용)
from config.cors_settings import get_security_settings, validate_and_log_cors

# 통합 보안 설정 로드
security_config = get_security_settings()

# CORS 설정
CORS_ALLOWED_ORIGINS = security_config['CORS_ALLOWED_ORIGINS']
CORS_ALLOW_ALL_ORIGINS = security_config['CORS_ALLOW_ALL_ORIGINS']
CORS_ALLOW_CREDENTIALS = security_config['CORS_ALLOW_CREDENTIALS']
CORS_ALLOW_HEADERS = security_config['CORS_ALLOW_HEADERS']
CORS_ALLOW_METHODS = security_config['CORS_ALLOW_METHODS']

# CSRF 설정
CSRF_TRUSTED_ORIGINS = security_config['CSRF_TRUSTED_ORIGINS']

# CORS 설정 검증 및 로깅
validate_and_log_cors()

# 로깅 설정 (Cloud Logging)
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': os.getenv('LOG_LEVEL', 'INFO'),
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Google Cloud Logging 설정 (선택사항)
try:
    from google.cloud import logging as cloud_logging
    
    client = cloud_logging.Client(project=GCP_PROJECT_ID)
    client.setup_logging()
    print("✅ Google Cloud Logging 설정 완료")
    
except Exception as e:
    print(f"⚠️ Google Cloud Logging 설정 실패: {e}")
    # Google Cloud Logging이 설치되지 않은 경우 무시
    pass

# 이메일 설정 (선택사항)
if os.getenv('EMAIL_HOST'):
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.getenv('EMAIL_HOST')
    EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
    EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
    EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
    EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
    DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@dental-ai.com')

# 성능 최적화
CONN_MAX_AGE = 60  # 데이터베이스 연결 재사용

# 미들웨어 최적화
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 정적 파일 서빙
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# 압축 설정
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# API 설정
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
})

# 헬스 체크 설정
HEALTH_CHECK = {
    'DISK_USAGE_MAX': 90,  # 디스크 사용률 90% 이하
    'MEMORY_MIN': 100,     # 최소 100MB 메모리
}

# 모니터링 설정
MONITORING = {
    'ENABLE_METRICS': True,
    'METRICS_ENDPOINT': '/metrics/',
    'HEALTH_ENDPOINT': '/health/',
}

print(f"✅ 프로덕션 설정 로드 완료 - 프로젝트: {GCP_PROJECT_ID}, 리전: {GCP_REGION}")