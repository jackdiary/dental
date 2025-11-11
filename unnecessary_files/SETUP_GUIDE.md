# 치과 추천 AI 시스템 설치 및 실행 가이드

## 📋 목차
1. [시스템 요구사항](#시스템-요구사항)
2. [설치 방법](#설치-방법)
3. [실행 방법](#실행-방법)
4. [추가 작업 필요 사항](#추가-작업-필요-사항)
5. [API 사용법](#api-사용법)
6. [문제 해결](#문제-해결)

## 🔧 시스템 요구사항

### 필수 소프트웨어
- **Python 3.11+**
- **PostgreSQL 15+**
- **Redis 7+**
- **Chrome/Chromium** (크롤링용)
- **Git**

### 선택적 소프트웨어
- **Docker & Docker Compose** (컨테이너 실행용)
- **KoNLPy** (한국어 형태소 분석용)

## 🚀 설치 방법

### 방법 1: Docker 사용 (권장)

```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd dental-recommendation-ai

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일을 편집하여 필요한 설정 변경

# 3. Docker Compose로 실행
docker-compose up -d

# 4. 데이터베이스 마이그레이션
docker-compose exec web python manage.py migrate

# 5. 슈퍼유저 생성
docker-compose exec web python manage.py createsuperuser

# 6. 초기 데이터 설정
docker-compose exec web python manage.py setup_initial_data --create-superuser --create-sample-data
```

### 방법 2: 로컬 설치

```bash
# 1. 프로젝트 클론
git clone <repository-url>
cd dental-recommendation-ai

# 2. 가상환경 생성 및 활성화
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. PostgreSQL 데이터베이스 생성
createdb dental_ai

# 5. Redis 서버 시작
redis-server

# 6. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 7. 데이터베이스 마이그레이션
python manage.py makemigrations
python manage.py migrate

# 8. 슈퍼유저 생성
python manage.py createsuperuser

# 9. 초기 데이터 설정
python manage.py setup_initial_data --create-sample-data
```

## ▶️ 실행 방법

### Docker 환경

```bash
# 전체 서비스 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f web

# 서비스 중지
docker-compose down
```

### 로컬 환경

```bash
# 터미널 1: Django 개발 서버
python manage.py runserver

# 터미널 2: Celery Worker
celery -A config worker -l info

# 터미널 3: Celery Beat (스케줄러)
celery -A config beat -l info

# 터미널 4: Redis (이미 실행 중이 아닌 경우)
redis-server
```

## 🔍 시스템 검증

```bash
# 설정 검증 스크립트 실행
python scripts/verify_setup.py

# 테스트 실행
python manage.py test

# API 상태 확인
curl http://localhost:8000/api/health/
```

## ⚠️ 추가 작업 필요 사항

### 1. 크롤링 설정

#### Chrome WebDriver 설치
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install -y wget gnupg
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google.list
sudo apt-get update
sudo apt-get install -y google-chrome-stable

# macOS (Homebrew)
brew install --cask google-chrome
brew install chromedriver

# Windows
# Chrome 브라우저 설치 후 ChromeDriver 다운로드
# https://chromedriver.chromium.org/
```

#### 크롤링 제한 설정
```python
# config/settings.py에 추가
CRAWLING_DELAY_SECONDS = 3  # 요청 간 지연 시간
MAX_REVIEWS_PER_CLINIC = 500  # 치과당 최대 리뷰 수
CRAWLING_TIMEOUT = 30  # 타임아웃 (초)
```

### 2. 머신러닝 모델 설정

#### KoNLPy 설치 (한국어 형태소 분석)
```bash
# Ubuntu/Debian
sudo apt-get install g++ openjdk-8-jdk python3-dev python3-pip curl
pip install konlpy

# macOS
brew install openjdk@8
pip install konlpy

# Windows
# Java JDK 8+ 설치 필요
pip install konlpy
```

#### 감성 분석 모델 훈련 (선택사항)
```bash
# 기본 SVM 모델 사용 (별도 훈련 불필요)
# KoBERT 모델 사용 시 추가 설정 필요
pip install transformers torch
```

### 3. 외부 API 설정 (선택사항)

#### 네이버 개발자 API
```bash
# .env 파일에 추가
NAVER_CLIENT_ID=your_client_id
NAVER_CLIENT_SECRET=your_client_secret
```

#### 구글 Places API
```bash
# .env 파일에 추가
GOOGLE_PLACES_API_KEY=your_api_key
```

### 4. 프로덕션 설정

#### 보안 설정
```python
# config/settings.py 프로덕션 설정
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com']
SECRET_KEY = 'your-production-secret-key'

# HTTPS 설정
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

#### 데이터베이스 최적화
```sql
-- PostgreSQL 인덱스 최적화
CREATE INDEX CONCURRENTLY idx_reviews_clinic_processed ON reviews_review(clinic_id, is_processed);
CREATE INDEX CONCURRENTLY idx_reviews_search_vector ON reviews_review USING GIN(search_vector);
```

## 📡 API 사용법

### 인증
```bash
# 사용자 등록
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "testpass123",
    "password_confirm": "testpass123"
  }'

# 로그인
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'
```

### 크롤링 (관리자 권한 필요)
```bash
# 단일 치과 크롤링
curl -X POST http://localhost:8000/api/reviews/crawl/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clinic_id": 1,
    "source": "naver",
    "max_reviews": 100
  }'

# 크롤링 상태 확인
curl -X GET http://localhost:8000/api/reviews/crawl/status/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 리뷰 조회
```bash
# 치과 리뷰 조회
curl -X GET http://localhost:8000/api/reviews/clinic/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## 🔧 관리자 기능

### Django Admin 접속
```
URL: http://localhost:8000/admin/
계정: 생성한 슈퍼유저 계정 사용
```

### 주요 관리 기능
- **치과 정보 관리**: 치과 등록, 수정, 삭제
- **리뷰 관리**: 리뷰 상태 변경, 플래그 처리
- **크롤링 모니터링**: 크롤링 상태 및 통계 확인
- **사용자 관리**: 사용자 권한 및 프리미엄 설정

## 🐛 문제 해결

### 일반적인 문제들

#### 1. 크롤링 실패
```bash
# Chrome/ChromeDriver 버전 확인
google-chrome --version
chromedriver --version

# 권한 문제 해결
sudo chmod +x /usr/bin/chromedriver
```

#### 2. 데이터베이스 연결 오류
```bash
# PostgreSQL 서비스 상태 확인
sudo systemctl status postgresql

# 데이터베이스 연결 테스트
psql -h localhost -U postgres -d dental_ai
```

#### 3. Redis 연결 오류
```bash
# Redis 서비스 상태 확인
redis-cli ping

# Redis 서버 시작
redis-server
```

#### 4. Celery 작업 실패
```bash
# Celery 워커 상태 확인
celery -A config inspect active

# 실패한 작업 확인
celery -A config events
```

### 로그 확인
```bash
# Django 로그
tail -f logs/django.log

# Celery 로그
celery -A config worker -l debug

# Docker 로그
docker-compose logs -f web
docker-compose logs -f celery
```

## 📊 성능 모니터링

### 시스템 상태 확인
```bash
# API 응답 시간 측정
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/health/

# 데이터베이스 성능 확인
python manage.py dbshell
\timing on
SELECT COUNT(*) FROM reviews_review;
```

### 메모리 및 CPU 사용량
```bash
# Docker 환경
docker stats

# 로컬 환경
htop
```

## 🔄 정기 유지보수

### 일일 작업
```bash
# 로그 파일 정리
find logs/ -name "*.log" -mtime +7 -delete

# 임시 파일 정리
python manage.py clearsessions
```

### 주간 작업
```bash
# 데이터베이스 백업
pg_dump dental_ai > backup_$(date +%Y%m%d).sql

# 성능 통계 업데이트
python manage.py update_statistics
```

## 📞 지원 및 문의

- **이슈 리포트**: GitHub Issues
- **문서**: 프로젝트 README.md
- **API 문서**: http://localhost:8000/api/docs/ (구현 시)

---

이 가이드를 따라 시스템을 설치하고 실행하면 치과 추천 AI 시스템을 완전히 활용할 수 있습니다.