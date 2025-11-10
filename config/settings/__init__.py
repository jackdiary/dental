"""
Django 설정 패키지
환경별 설정을 관리합니다.
"""

import os

# 환경 변수에서 설정 모듈 결정
ENVIRONMENT = os.getenv('DJANGO_SETTINGS_MODULE', 'config.settings.development')

if 'production' in ENVIRONMENT:
    from .production import *
elif 'staging' in ENVIRONMENT:
    from .staging import *
else:
    from .development import *