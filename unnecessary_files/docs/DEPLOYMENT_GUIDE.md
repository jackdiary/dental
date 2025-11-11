# 🚀 치과 추천 AI 배포 가이드

## 📋 배포 개요

이 가이드는 치과 추천 AI 시스템을 Google Cloud Platform (GCP)에 배포하는 방법을 설명합니다.

---

## 🏗️ 배포 아키텍처

### GCP 서비스 구성
```
Internet → Cloud Load Balancer → Cloud Run (Frontend)
                ↓
         Cloud Run (Backend) → Cloud SQL (PostgreSQL)
                ↓
         Cloud Storage (정적 파일)
                ↓
         Cloud Logging & Monitoring
```

### 서비스 구성요소
- **Cloud Run**: 컨테이너 기반 서버리스 플랫폼
- **Cloud SQL**: 관리형 PostgreSQL 데이터베이스
- **Cloud Storage**: 정적 파일 저장소
- **Cloud Load Balancer**: 로드 밸런싱 및 SSL 종료
- **Cloud Build**: CI/CD 파이프라인
- **Container Registry**: Docker 이미지 저장소

---

## 🔧 사전 준비

### 1. GCP 프로젝트 설정
```bash
# GCP CLI 설치 및 인증
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 필요한 API 활성화
gcloud services enable run.googleapis.com
gcloud services enable sql-component.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable storage-component.googleapis.com
```

### 2. 환경 변수 설정
```bash
export PROJECT_ID="your-project-id"
export REGION="asia-northeast3"  # 서울 리전
export SERVICE_NAME="dental-ai"
export DB_INSTANCE_NAME="dental-ai-db"
```

---

## 🐳 Docker 컨테이너 준비

### 1. 백엔드 Dockerfile
```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# 시스템 패키지 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 정적 파일 수집
RUN python manage.py collectstatic --noinput

# 포트 설정
EXPOSE 8080

# 서버 시작
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 config.wsgi:application
```

### 2. 프론트엔드 Dockerfile
```dockerfile
# frontend/Dockerfile
FROM node:18-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Nginx로 정적 파일 서빙
FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### 3. Nginx 설정
```nginx
# frontend/nginx.conf
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        location / {
            try_files $uri $uri/ /index.html;
        }

        location /api/ {
            proxy_pass http://backend-service:8080;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## 🗄️ 데이터베이스 설정

### 1. Cloud SQL 인스턴스 생성
```bash
# PostgreSQL 인스턴스 생성
gcloud sql instances create $DB_INSTANCE_NAME \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=10GB

# 데이터베이스 생성
gcloud sql databases create dental_ai_db \
    --instance=$DB_INSTANCE_NAME

# 사용자 생성
gcloud sql users create dental_ai_user \
    --instance=$DB_INSTANCE_NAME \
    --password=YOUR_SECURE_PASSWORD
```

### 2. 데이터베이스 연결 설정
```python
# config/settings_production.py
import os
from google.cloud.sql.connector import Connector

# Cloud SQL 연결 설정
def getconn():
    connector = Connector()
    conn = connector.connect(
        f"{os.environ['PROJECT_ID']}:{os.environ['REGION']}:{os.environ['DB_INSTANCE_NAME']}",
        "pg8000",
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        db=os.environ["DB_NAME"]
    )
    return conn

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'dental_ai_db'),
        'USER': os.environ.get('DB_USER', 'dental_ai_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': '127.0.0.1',
        'PORT': '5432',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Cloud SQL Proxy 사용 시
if os.environ.get('USE_CLOUD_SQL_AUTH_PROXY'):
    DATABASES['default']['HOST'] = '127.0.0.1'
    DATABASES['default']['PORT'] = '5432'
```

---

## 🚀 Cloud Run 배포

### 1. 백엔드 배포
```bash
# Docker 이미지 빌드 및 푸시
gcloud builds submit --tag gcr.io/$PROJECT_ID/dental-ai-backend

# Cloud Run 서비스 배포
gcloud run deploy dental-ai-backend \
    --image gcr.io/$PROJECT_ID/dental-ai-backend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="DJANGO_SETTINGS_MODULE=config.settings_production" \
    --set-env-vars="PROJECT_ID=$PROJECT_ID" \
    --set-env-vars="DB_NAME=dental_ai_db" \
    --set-env-vars="DB_USER=dental_ai_user" \
    --set-env-vars="DB_PASSWORD=YOUR_SECURE_PASSWORD" \
    --set-env-vars="DB_INSTANCE_NAME=$DB_INSTANCE_NAME" \
    --add-cloudsql-instances $PROJECT_ID:$REGION:$DB_INSTANCE_NAME \
    --memory 2Gi \
    --cpu 1 \
    --max-instances 10
```

### 2. 프론트엔드 배포
```bash
# 프론트엔드 빌드 및 배포
cd frontend
gcloud builds submit --tag gcr.io/$PROJECT_ID/dental-ai-frontend

gcloud run deploy dental-ai-frontend \
    --image gcr.io/$PROJECT_ID/dental-ai-frontend \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --port 80 \
    --memory 512Mi \
    --cpu 1
```

---

## 🔄 CI/CD 파이프라인

### 1. GitHub Actions 워크플로우
```yaml
# .github/workflows/deploy.yml
name: Deploy to Cloud Run

on:
  push:
    branches: [ main ]

env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  REGION: asia-northeast3
  SERVICE_NAME: dental-ai

jobs:
  deploy-backend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
      with:
        project_id: ${{ secrets.GCP_PROJECT_ID }}
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        export_default_credentials: true

    - name: Configure Docker
      run: gcloud auth configure-docker

    - name: Build and Push Backend
      run: |
        docker build -t gcr.io/$PROJECT_ID/dental-ai-backend .
        docker push gcr.io/$PROJECT_ID/dental-ai-backend

    - name: Deploy Backend to Cloud Run
      run: |
        gcloud run deploy dental-ai-backend \
          --image gcr.io/$PROJECT_ID/dental-ai-backend \
          --platform managed \
          --region $REGION \
          --allow-unauthenticated

  deploy-frontend:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'

    - name: Build Frontend
      run: |
        cd frontend
        npm ci
        npm run build

    - name: Deploy Frontend to Cloud Run
      run: |
        cd frontend
        gcloud builds submit --tag gcr.io/$PROJECT_ID/dental-ai-frontend
        gcloud run deploy dental-ai-frontend \
          --image gcr.io/$PROJECT_ID/dental-ai-frontend \
          --platform managed \
          --region $REGION \
          --allow-unauthenticated
```

### 2. Cloud Build 설정
```yaml
# cloudbuild.yaml
steps:
# 백엔드 빌드
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/dental-ai-backend', '.']

# 백엔드 푸시
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/dental-ai-backend']

# 백엔드 배포
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: gcloud
  args:
  - 'run'
  - 'deploy'
  - 'dental-ai-backend'
  - '--image'
  - 'gcr.io/$PROJECT_ID/dental-ai-backend'
  - '--region'
  - 'asia-northeast3'
  - '--platform'
  - 'managed'
  - '--allow-unauthenticated'

# 프론트엔드 빌드
- name: 'node:18'
  entrypoint: 'bash'
  args:
  - '-c'
  - |
    cd frontend
    npm ci
    npm run build

# 프론트엔드 Docker 빌드
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/dental-ai-frontend', './frontend']

# 프론트엔드 배포
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: gcloud
  args:
  - 'run'
  - 'deploy'
  - 'dental-ai-frontend'
  - '--image'
  - 'gcr.io/$PROJECT_ID/dental-ai-frontend'
  - '--region'
  - 'asia-northeast3'
  - '--platform'
  - 'managed'
  - '--allow-unauthenticated'

images:
- 'gcr.io/$PROJECT_ID/dental-ai-backend'
- 'gcr.io/$PROJECT_ID/dental-ai-frontend'
```

---

## 🔒 보안 설정

### 1. IAM 권한 설정
```bash
# 서비스 계정 생성
gcloud iam service-accounts create dental-ai-service \
    --display-name="Dental AI Service Account"

# 필요한 권한 부여
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:dental-ai-service@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudsql.client"

gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:dental-ai-service@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.objectViewer"
```

### 2. 환경 변수 보안
```bash
# Secret Manager 사용
gcloud secrets create db-password --data-file=password.txt
gcloud secrets create django-secret-key --data-file=secret-key.txt

# Cloud Run에서 시크릿 사용
gcloud run services update dental-ai-backend \
    --update-secrets="DB_PASSWORD=db-password:latest" \
    --update-secrets="SECRET_KEY=django-secret-key:latest"
```

### 3. SSL/TLS 설정
```bash
# 커스텀 도메인 매핑
gcloud run domain-mappings create \
    --service dental-ai-frontend \
    --domain your-domain.com \
    --region $REGION
```

---

## 📊 모니터링 및 로깅

### 1. Cloud Logging 설정
```python
# config/settings_production.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
```

### 2. 헬스 체크 설정
```python
# apps/api/views.py
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    try:
        # 데이터베이스 연결 확인
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({
            'status': 'healthy',
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'error': str(e)
        }, status=500)
```

### 3. 메트릭 수집
```bash
# Cloud Monitoring 알림 설정
gcloud alpha monitoring policies create \
    --policy-from-file=monitoring-policy.yaml
```

---

## 🔄 데이터베이스 마이그레이션

### 1. 초기 마이그레이션
```bash
# Cloud Run Job으로 마이그레이션 실행
gcloud run jobs create migrate-job \
    --image gcr.io/$PROJECT_ID/dental-ai-backend \
    --region $REGION \
    --task-timeout 3600 \
    --command "python,manage.py,migrate" \
    --add-cloudsql-instances $PROJECT_ID:$REGION:$DB_INSTANCE_NAME

gcloud run jobs execute migrate-job --region $REGION
```

### 2. 더미 데이터 생성
```bash
# 더미 데이터 생성 Job
gcloud run jobs create create-data-job \
    --image gcr.io/$PROJECT_ID/dental-ai-backend \
    --region $REGION \
    --task-timeout 3600 \
    --command "python,scripts/create_final_dummy_data.py" \
    --add-cloudsql-instances $PROJECT_ID:$REGION:$DB_INSTANCE_NAME

gcloud run jobs execute create-data-job --region $REGION
```

---

## 📈 성능 최적화

### 1. Cloud CDN 설정
```bash
# 정적 파일용 CDN 설정
gcloud compute backend-buckets create dental-ai-static \
    --gcs-bucket-name=dental-ai-static-files

gcloud compute url-maps create dental-ai-lb \
    --default-service=dental-ai-frontend
```

### 2. 캐싱 전략
```python
# Redis 캐시 설정 (Cloud Memorystore)
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': f'redis://{os.environ.get("REDIS_HOST")}:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

---

## 🚨 장애 대응

### 1. 롤백 전략
```bash
# 이전 버전으로 롤백
gcloud run services update-traffic dental-ai-backend \
    --to-revisions=dental-ai-backend-00001-abc=100

# 점진적 배포
gcloud run services update-traffic dental-ai-backend \
    --to-revisions=dental-ai-backend-00002-def=50,dental-ai-backend-00001-abc=50
```

### 2. 백업 및 복구
```bash
# 데이터베이스 백업
gcloud sql backups create \
    --instance=$DB_INSTANCE_NAME \
    --description="Pre-deployment backup"

# 백업에서 복구
gcloud sql backups restore BACKUP_ID \
    --restore-instance=$DB_INSTANCE_NAME
```

---

## 💰 비용 최적화

### 1. 리소스 최적화
- **Cloud Run**: 요청 기반 과금으로 비용 효율적
- **Cloud SQL**: 필요에 따라 인스턴스 크기 조정
- **Cloud Storage**: 라이프사이클 정책으로 오래된 파일 삭제

### 2. 모니터링 도구
```bash
# 비용 알림 설정
gcloud billing budgets create \
    --billing-account=BILLING_ACCOUNT_ID \
    --display-name="Dental AI Budget" \
    --budget-amount=100USD
```

---

## 📋 배포 체크리스트

### 배포 전
- [ ] 환경 변수 설정 확인
- [ ] 데이터베이스 연결 테스트
- [ ] 보안 설정 검토
- [ ] 백업 생성

### 배포 중
- [ ] 빌드 성공 확인
- [ ] 헬스 체크 통과
- [ ] 로그 모니터링
- [ ] 성능 테스트

### 배포 후
- [ ] 기능 테스트
- [ ] 모니터링 설정
- [ ] 알림 확인
- [ ] 문서 업데이트

---

이 가이드를 따라 하면 치과 추천 AI 시스템을 안전하고 효율적으로 GCP에 배포할 수 있습니다.