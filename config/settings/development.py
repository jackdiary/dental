"""
Django 개발 환경 설정
로컬 개발용 설정
"""

from decouple import config
from .base import *

# 기본 설정
DEBUG = True
ENVIRONMENT = 'development'

# 보안 설정 (개발용)
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production')

# 허용된 호스트
ALLOWED_HOSTS = config(
    'ALLOWED_HOSTS', 
    default='localhost,127.0.0.1,testserver', 
    cast=lambda v: [s.strip() for s in v.split(',')]
)

# 데이터베이스 설정
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='dental_ai'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default='password'),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'OPTIONS': {
            'client_encoding': 'UTF8',
        },
    }
}

# Cache Configuration (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://127.0.0.1:6379/1'),
    }
}

# Celery Configuration
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://127.0.0.1:6379/0')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://127.0.0.1:6379/0')

# CORS 설정 (CORS 유틸리티 모듈 사용)
from config.cors_settings import get_cors_settings, validate_and_log_cors

# CORS 설정 로드
cors_config = get_cors_settings()
CORS_ALLOWED_ORIGINS = cors_config['CORS_ALLOWED_ORIGINS']
CORS_ALLOW_ALL_ORIGINS = cors_config['CORS_ALLOW_ALL_ORIGINS']
CORS_ALLOW_CREDENTIALS = cors_config['CORS_ALLOW_CREDENTIALS']
CORS_ALLOW_HEADERS = cors_config['CORS_ALLOW_HEADERS']
CORS_ALLOW_METHODS = cors_config['CORS_ALLOW_METHODS']

# CORS 설정 검증 및 로깅
validate_and_log_cors()

# 개발용 도구
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
INTERNAL_IPS = ['127.0.0.1']

# 로깅 설정 (개발용)
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
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': LOGS_DIR / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

print("🔧 개발 환경 설정 로드 완료")