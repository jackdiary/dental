# 치과 추천 AI 시스템 - 사전 설정 요구사항

## 필수 설정 항목

### 1. PostgreSQL 데이터베이스
```bash
# Windows에서 PostgreSQL 설치
# https://www.postgresql.org/download/windows/

# 데이터베이스 생성
createdb dental_ai

# 사용자 생성 (선택사항)
createuser --interactive dental_user
```

**환경변수 설정 (.env 파일)**:
```
DB_NAME=dental_ai
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
```

### 2. Redis 서버
```bash
# Windows에서 Redis 설치
# https://github.com/microsoftarchive/redis/releases

# Redis 실행
redis-server
```

**환경변수 설정**:
```
REDIS_URL=redis://127.0.0.1:6379/1
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
```

### 3. Celery 워커 (비동기 크롤링용)
```bash
# 별도 터미널에서 실행
celery -A config worker --loglevel=info

# Windows에서는
celery -A config worker --loglevel=info --pool=solo
```

## 선택사항 설정

### 4. Java 환경 (KoNLPy 완전 기능)
```bash
# Java 8+ 설치
# https://www.oracle.com/java/technologies/downloads/

# JAVA_HOME 환경변수 설정
set JAVA_HOME=C:\Program Files\Java\jdk-11.0.x
```

### 5. 외부 API 키

#### 네이버 개발자 센터
1. https://developers.naver.com/main/ 접속
2. 애플리케이션 등록
3. Client ID, Client Secret 발급

#### 구글 Places API
1. https://console.cloud.google.com/ 접속
2. Places API 활성화
3. API 키 발급

**환경변수 설정**:
```
NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
GOOGLE_PLACES_API_KEY=your_google_api_key
```

## 설정 순서 권장사항

1. **PostgreSQL 설치 및 설정** (필수)
2. **Redis 설치 및 실행** (필수)
3. **데이터베이스 마이그레이션 실행**
4. **Celery 워커 실행** (크롤링 기능용)
5. **외부 API 키 설정** (실제 크롤링용)
6. **Java 설치** (고급 NLP 기능용)

## 현재 상태 확인

### 설치된 것들 ✅
- Python 가상환경
- Django 및 필수 패키지들
- React 프론트엔드
- Selenium WebDriver

### 아직 설정 안된 것들 ❌
- PostgreSQL 데이터베이스
- Redis 서버
- Celery 워커
- 외부 API 키들
- Java 환경

## 빠른 시작 (최소 설정)

PostgreSQL과 Redis만 설치하면 기본 기능들은 모두 동작합니다:

1. PostgreSQL 설치 → 데이터베이스 생성
2. Redis 설치 → 서버 실행
3. 환경변수 설정 (.env 파일)
4. 마이그레이션 실행: `python manage.py migrate`
5. 서버 실행: `python manage.py runserver`

나머지는 필요에 따라 나중에 추가 설정 가능합니다.