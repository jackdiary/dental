#!/usr/bin/env python
"""
Script to verify the Django project setup
"""
import os
import sys
import django
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    django.setup()
    print("✅ Django setup successful")
except Exception as e:
    print(f"❌ Django setup failed: {e}")
    sys.exit(1)

# Test imports
try:
    from apps.accounts.models import User
    from apps.clinics.models import Clinic
    from apps.reviews.models import Review
    from apps.analysis.models import SentimentAnalysis, PriceData
    from apps.recommendations.models import RecommendationLog
    print("✅ All models imported successfully")
except ImportError as e:
    print(f"❌ Model import failed: {e}")
    sys.exit(1)

# Test database connection
try:
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    print("✅ Database connection successful")
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("Make sure PostgreSQL is running and configured correctly")

# Test Redis connection (optional)
try:
    from django.core.cache import cache
    cache.set('test_key', 'test_value', 30)
    if cache.get('test_key') == 'test_value':
        print("✅ Redis connection successful")
    else:
        print("⚠️  Redis connection issue")
except Exception as e:
    print(f"⚠️  Redis connection failed: {e}")
    print("Redis is optional but recommended for production")

# Test Celery configuration
try:
    from config.celery import app as celery_app
    print("✅ Celery configuration loaded")
except Exception as e:
    print(f"❌ Celery configuration failed: {e}")

print("\n🎉 Project setup verification completed!")
print("\nNext steps:")
print("1. Run migrations: python manage.py migrate")
print("2. Create superuser: python manage.py createsuperuser")
print("3. Start development server: python manage.py runserver")
print("4. Start Celery worker: celery -A config worker -l info")
print("\n📊 Additional verification:")
print("- Run performance tests: python test_performance.py")
print("- View API documentation: http://localhost:8000/api/swagger/")
print("- Check system status: Access admin panel for monitoring")