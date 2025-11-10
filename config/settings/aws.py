"""
Django AWS EC2 배포 설정
"""
from .base import *
import os

# 기본 설정
DEBUG = os.getenv('DEBUG', 'False') == 'True'
ENVIRONMENT = 'aws'

# AWS EC2 설정
AWS_EC2_IP = os.getenv('AWS_EC2_IP', '3.36.129.103')

# 보안 설정
SECRET_KEY = os.getenv('SECRET_KEY', 'dental-ai-aws-secret-key-2024-change-in-production')

# 허용된 호스트
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', f'{AWS_EC2_IP},localhost,127.0.0.1').split(',')

# 데이터베이스 설정 (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'dental_ai'),
        'USER': os.getenv('DB_USER', 'dental_user'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'dental_password_2024'),
        'HOST': os.getenv('DB_HOST', 'db'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

# Redis 설정
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_URL = os.getenv('REDIS_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/1')

# 캐시 설정
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Celery 설정
CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', f'redis://{REDIS_HOST}:{REDIS_PORT}/0')

# CORS 설정
cors_origins = os.getenv('CORS_ALLOWED_ORIGINS', '')
if cors_origins:
    CORS_ALLOWED_ORIGINS = [origin.strip() for origin in cors_origins.split(',')]
else:
    CORS_ALLOWED_ORIGINS = [
        f'http://{AWS_EC2_IP}',
        f'http://{AWS_EC2_IP}:3000',
        f'http://{AWS_EC2_IP}:8000',
        'http://localhost:3000',
        'http://localhost:5173',
    ]

CORS_ALLOW_ALL_ORIGINS = DEBUG  # DEBUG 모드에서만 모든 오리진 허용
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF 설정
CSRF_TRUSTED_ORIGINS = [
    f'http://{AWS_EC2_IP}',
    f'http://{AWS_EC2_IP}:3000',
    f'http://{AWS_EC2_IP}:8000',
]

# 보안 헤더 설정 (HTTP용)
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Cross-Origin 정책 완화
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# 정적 파일 설정
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# 로깅 설정
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}

print(f"✅ AWS EC2 설정 로드 완료 - IP: {AWS_EC2_IP}")
