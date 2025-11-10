# Google App Engine 진입점
import os
from django.core.wsgi import get_wsgi_application

# 프로덕션 설정 사용
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings_production')

application = get_wsgi_application()