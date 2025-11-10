# 로컬 개발 환경 설정 가이드

## 1. Google Cloud SDK 설치

### 1.1 Windows에서 설치
1. [Google Cloud SDK 다운로드](https://cloud.google.com/sdk/docs/install) 페이지 접속
2. Windows용 설치 프로그램 다운로드
3. 설치 프로그램 실행 후 기본 설정으로 설치
4. 설치 완료 후 명령 프롬프트 재시작

### 1.2 설치 확인
```bash
gcloud version
```

### 1.3 Google Cloud 인증
```bash
# Google 계정으로 로그인
gcloud auth login

# 애플리케이션 기본 자격 증명 설정
gcloud auth application-default login

# 프로젝트 설정
gcloud config set project dental-ai-2024

# 기본 리전 설정
gcloud config set compute/region asia-northeast3
gcloud config set compute/zone asia-northeast3-a
```

## 2. Docker Desktop 설치

### 2.1 Docker Desktop 다운로드 및 설치
1. [Docker Desktop](https://www.docker.com/products/docker-desktop/) 다운로드
2. 설치 프로그램 실행
3. WSL 2 백엔드 사용 설정 (Windows)
4. 설치 완료 후 Docker Desktop 실행

### 2.2 Docker 설치 확인
```bash
docker --version
docker-compose --version
```

### 2.3 Docker 테스트
```bash
docker run hello-world
```

## 3. 필요한 도구 설치

### 3.1 Node.js (프론트엔드 빌드용)
```bash
# Node.js 18 LTS 설치 확인
node --version
npm --version
```

### 3.2 Python (백엔드 개발용)
```bash
# Python 3.11 설치 확인
python --version
pip --version
```

### 3.3 Git (버전 관리)
```bash
git --version
```

## 4. 환경 변수 파일 생성

### 4.1 프로덕션 환경 변수 파일 생성
```bash
# 프로젝트 루트에 .env.production 파일 생성
touch .env.production
```

### 4.2 .env.production 템플릿
```bash
# Google Cloud 프로젝트 설정
GCP_PROJECT_ID=dental-ai-2024
GCP_REGION=asia-northeast3
GCP_ZONE=asia-northeast3-a

# Django 설정
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,*.run.app

# 데이터베이스 설정 (나중에 Cloud SQL 생성 후 업데이트)
DATABASE_URL=postgresql://username:password@/dbname?host=/cloudsql/project:region:instance

# Redis 설정 (나중에 Memorystore 생성 후 업데이트)
REDIS_URL=redis://10.0.0.3:6379/0

# Cloud Storage 설정
GS_BUCKET_NAME=dental-ai-static-files
GS_PROJECT_ID=dental-ai-2024

# 보안 설정
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS=True
SECURE_HSTS_PRELOAD=True

# CORS 설정
CORS_ALLOWED_ORIGINS=https://your-domain.com
CORS_ALLOW_CREDENTIALS=True

# 로깅 설정
LOG_LEVEL=INFO
GOOGLE_CLOUD_PROJECT=dental-ai-2024
```

## 5. 프로젝트 구조 정리

### 5.1 배포 디렉토리 생성
```bash
mkdir -p deploy/{docker,kubernetes,scripts}
mkdir -p deploy/config/{nginx,gunicorn}
```

### 5.2 .gitignore 업데이트
```bash
# .gitignore에 추가할 내용
echo "
# Google Cloud
.gcloud/
service-account-key.json

# Environment files
.env.production
.env.local

# Docker
.dockerignore

# Build artifacts
dist/
build/
*.tar.gz
" >> .gitignore
```

## 6. 개발 환경 확인

### 6.1 Google Cloud 연결 테스트
```bash
# 프로젝트 정보 확인
gcloud projects describe dental-ai-2024

# 활성화된 API 확인
gcloud services list --enabled

# 현재 인증 정보 확인
gcloud auth list
```

### 6.2 Docker 연결 테스트
```bash
# Container Registry 인증 설정
gcloud auth configure-docker

# 테스트 이미지 빌드 (선택사항)
docker build -t test-image .
```

## 7. IDE 설정 (선택사항)

### 7.1 VS Code 확장 프로그램
- Google Cloud Code
- Docker
- Python
- JavaScript/TypeScript

### 7.2 환경 변수 설정
VS Code에서 `.env.production` 파일을 인식하도록 설정

## 다음 단계

로컬 환경 설정이 완료되면:
1. **Django 프로덕션 설정** 생성
2. **백엔드 Dockerfile** 작성
3. **프론트엔드 빌드 설정** 구성

---

**⚠️ 주의사항**
- `.env.production` 파일은 절대 Git에 커밋하지 마세요
- Google Cloud 자격 증명은 안전하게 보관하세요
- Docker Desktop이 실행 중인지 확인하세요