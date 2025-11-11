# 🚀 빠른 시작 가이드

## 5분 만에 시스템 실행하기

### 1️⃣ 사전 준비 (1분)
```bash
# 필수 소프트웨어 확인
python --version  # 3.11+ 필요
docker --version  # Docker 설치 확인
git --version     # Git 설치 확인
```

### 2️⃣ 프로젝트 설정 (2분)
```bash
# 프로젝트 클론
git clone <repository-url>
cd dental-recommendation-ai

# 환경 변수 복사
cp .env.example .env

# Docker로 전체 시스템 시작
docker-compose up -d
```

### 3️⃣ 초기 설정 (2분)
```bash
# 데이터베이스 마이그레이션
docker-compose exec web python manage.py migrate

# 관리자 계정 생성
docker-compose exec web python manage.py createsuperuser

# 샘플 데이터 생성
docker-compose exec web python manage.py setup_initial_data --create-sample-data
```

### 4️⃣ 시스템 확인 (30초)
```bash
# API 상태 확인
curl http://localhost:8000/api/health/

# 관리자 페이지 접속
# 브라우저에서 http://localhost:8000/admin/ 접속
```

## 🎯 주요 기능 테스트

### API 테스트
```bash
# 1. 사용자 등록
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com", 
    "password": "testpass123",
    "password_confirm": "testpass123"
  }'

# 2. 로그인 (토큰 받기)
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123"
  }'

# 3. 치과 리뷰 조회 (토큰 사용)
curl -X GET http://localhost:8000/api/reviews/clinic/1/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 관리자 기능 테스트
1. **http://localhost:8000/admin/** 접속
2. 생성한 관리자 계정으로 로그인
3. **Clinics** → **Clinics** 메뉴에서 치과 정보 확인
4. **Reviews** → **Reviews** 메뉴에서 리뷰 데이터 확인

## ⚡ 다음 단계

### 실제 데이터 수집하기
```bash
# 크롤링 시작 (관리자 토큰 필요)
curl -X POST http://localhost:8000/api/reviews/crawl/ \
  -H "Authorization: Bearer ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clinic_id": 1,
    "source": "naver",
    "max_reviews": 10
  }'
```

### 개발 환경 설정
```bash
# 로컬 개발용 (Docker 대신)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py runserver
```

## 🔧 문제 해결

### 일반적인 오류들
```bash
# Docker 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs web
docker-compose logs db

# 컨테이너 재시작
docker-compose restart web
```

### 포트 충돌 시
```bash
# docker-compose.yml에서 포트 변경
# ports: "8001:8000"  # 8000 대신 8001 사용
```

## 📚 추가 자료
- **상세 설치 가이드**: [SETUP_GUIDE.md](SETUP_GUIDE.md)
- **개발자 가이드**: [DEVELOPMENT_GUIDE.md](DEVELOPMENT_GUIDE.md)
- **API 문서**: http://localhost:8000/api/docs/ (구현 시)

---
**🎉 축하합니다! 치과 추천 AI 시스템이 성공적으로 실행되었습니다.**