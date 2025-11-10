# Google Cloud Platform 프로덕션 설정
import os
from .settings import *
from google.cloud import logging as cloud_logging

# 보안 설정
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# 데이터베이스 설정 (Cloud SQL)
if os.getenv('GAE_APPLICATION', None):
    # App Engine 환경
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME'),
            'USER': os.environ.get('DB_USER'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST'),
            'PORT': '5432',
            'OPTIONS': {
                'client_encoding': 'UTF8',
            },
        }
    }
else:
    # 로컬 개발 환경
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'dental_ai'),
            'USER': os.environ.get('DB_USER', 'dental_user'),
            'PASSWORD': os.environ.get('DB_PASSWORD'),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
        }
    }

# Redis 설정 (Cloud Memorystore)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
    }
}

# Celery 설정
CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND')

# 정적 파일 설정
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 미디어 파일 설정 (Cloud Storage)
if os.getenv('GAE_APPLICATION', None):
    DEFAULT_FILE_STORAGE = 'storages.backends.gcloud.GoogleCloudStorage'
    GS_BUCKET_NAME = os.environ.get('GS_BUCKET_NAME')
    MEDIA_URL = f'https://storage.googleapis.com/{GS_BUCKET_NAME}/'

# 로깅 설정 (Cloud Logging)
if os.getenv('GAE_APPLICATION', None):
    client = cloud_logging.Client()
    client.setup_logging()
    
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'cloud_logging': {
                'class': 'google.cloud.logging.handlers.CloudLoggingHandler',
                'client': client,
            },
        },
        'root': {
            'handlers': ['cloud_logging'],
            'level': 'INFO',
        },
    }

# 보안 헤더
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# HTTPS 설정 (프로덕션에서)
if os.getenv('GAE_APPLICATION', None):
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

# 외부 API 키
NAVER_CLIENT_ID = os.environ.get('NAVER_CLIENT_ID')
NAVER_CLIENT_SECRET = os.environ.get('NAVER_CLIENT_SECRET')
GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY')