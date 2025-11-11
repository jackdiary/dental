# 🚀 AWS EC2 배포 가이드

## 📋 목차
1. [빠른 시작](#빠른-시작)
2. [사전 요구사항](#사전-요구사항)
3. [배포 방법](#배포-방법)
4. [서비스 접속](#서비스-접속)
5. [문제 해결](#문제-해결)

## 🎯 빠른 시작

### 서버 정보
- **IP**: 3.36.129.103
- **OS**: Ubuntu
- **Docker**: 설치됨
- **프로젝트 경로**: `/home/ubuntu/hosptal`

### 1분 배포

```bash
# 1. 서버 접속
ssh -i your-key.pem ubuntu@3.36.129.103

# 2. 프로젝트 디렉토리로 이동
cd /home/ubuntu/hosptal

# 3. 최신 코드 가져오기 (이미 클론되어 있음)
git pull origin main

# 4. 배포 스크립트 실행
chmod +x deploy_aws_complete.sh
./deploy_aws_complete.sh
```

완료! 🎉

## 📦 사전 요구사항

### 서버 측
- ✅ Ubuntu 20.04 이상
- ✅ Docker 및 Docker Compose 설치됨
- ✅ Git 설치됨
- ✅ 포트 8000, 5432, 6379 오픈

### 로컬 측
- SSH 키 (서버 접속용)
- Git (코드 푸시용)

## 🔧 배포 방법

### 방법 1: 자동 배포 (권장)

완전 자동화된 배포 스크립트 사용:

```bash
./deploy_aws_complete.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
- ✅ 환경 변수 확인
- ✅ 기존 컨테이너 정리
- ✅ Docker 이미지 빌드
- ✅ 데이터베이스 시작
- ✅ 마이그레이션 실행
- ✅ 정적 파일 수집
- ✅ 모든 서비스 시작
- ✅ 상태 확인

### 방법 2: 빠른 업데이트

코드 변경 후 빠른 재배포:

```bash
./quick_deploy.sh
```

### 방법 3: 수동 배포

단계별 수동 배포:

```bash
# 1. 기존 컨테이너 중지
sudo docker compose -f docker-compose.aws.yml down

# 2. 이미지 빌드
sudo docker compose -f docker-compose.aws.yml build

# 3. 서비스 시작
sudo docker compose -f docker-compose.aws.yml up -d

# 4. 마이그레이션
sudo docker compose -f docker-compose.aws.yml exec web python manage.py migrate

# 5. 정적 파일 수집
sudo docker compose -f docker-compose.aws.yml exec web python manage.py collectstatic --noinput

# 6. 슈퍼유저 생성 (최초 1회)
sudo docker compose -f docker-compose.aws.yml exec web python manage.py createsuperuser
```

## 🌐 서비스 접속

### 백엔드 API
- **URL**: http://3.36.129.103:8000
- **관리자**: http://3.36.129.103:8000/admin
- **API 문서**: http://3.36.129.103:8000/api/docs
- **헬스체크**: http://3.36.129.103:8000/api/health/

### 데이터베이스
- **Host**: localhost (컨테이너 내부: db)
- **Port**: 5432
- **Database**: dental_ai
- **User**: dental_user
- **Password**: `.env.aws` 파일 참조

### Redis
- **Host**: localhost (컨테이너 내부: redis)
- **Port**: 6379

## 📊 서비스 관리

### 상태 확인

```bash
# 모든 컨테이너 상태
sudo docker compose -f docker-compose.aws.yml ps

# 특정 서비스 로그
sudo docker compose -f docker-compose.aws.yml logs -f web

# 리소스 사용량
sudo docker stats
```

### 서비스 제어

```bash
# 재시작
sudo docker compose -f docker-compose.aws.yml restart web

# 중지
sudo docker compose -f docker-compose.aws.yml stop

# 시작
sudo docker compose -f docker-compose.aws.yml start

# 완전 종료
sudo docker compose -f docker-compose.aws.yml down
```

### 컨테이너 접속

```bash
# 웹 서버
sudo docker exec -it hosptal-web bash

# 데이터베이스
sudo docker exec -it hosptal-db psql -U dental_user -d dental_ai

# Redis
sudo docker exec -it hosptal-redis redis-cli
```

## 🐛 문제 해결

### 500 Internal Server Error

**원인**: 서버 내부 오류

**해결**:
```bash
# 1. 로그 확인
sudo docker compose -f docker-compose.aws.yml logs web

# 2. 환경 변수 확인
sudo docker compose -f docker-compose.aws.yml exec web env | grep DJANGO

# 3. 데이터베이스 연결 확인
sudo docker compose -f docker-compose.aws.yml exec web python manage.py dbshell
```

### 400 Bad Request

**원인**: ALLOWED_HOSTS 설정 문제

**해결**:
```bash
# .env.aws 파일 수정
nano .env.aws

# ALLOWED_HOSTS 확인/수정
ALLOWED_HOSTS=3.36.129.103,localhost,127.0.0.1

# 재시작
sudo docker compose -f docker-compose.aws.yml restart web
```

### CORS 에러

**원인**: CORS 설정 문제

**해결**:
```bash
# .env.aws 파일 수정
nano .env.aws

# CORS_ALLOWED_ORIGINS 확인/수정
CORS_ALLOWED_ORIGINS=http://3.36.129.103:3000,http://3.36.129.103

# 재시작
sudo docker compose -f docker-compose.aws.yml restart web
```

### 데이터베이스 연결 실패

**원인**: PostgreSQL 컨테이너 문제

**해결**:
```bash
# 1. 데이터베이스 상태 확인
sudo docker compose -f docker-compose.aws.yml ps db

# 2. 데이터베이스 로그 확인
sudo docker compose -f docker-compose.aws.yml logs db

# 3. 데이터베이스 재시작
sudo docker compose -f docker-compose.aws.yml restart db

# 4. 완전 재시작 (주의: 데이터 손실 가능)
sudo docker compose -f docker-compose.aws.yml down -v
sudo docker compose -f docker-compose.aws.yml up -d
```

### 컨테이너가 계속 재시작됨

**원인**: 애플리케이션 크래시

**해결**:
```bash
# 1. 로그 확인
sudo docker compose -f docker-compose.aws.yml logs --tail=100 web

# 2. 컨테이너 내부 확인
sudo docker exec -it hosptal-web bash
python manage.py check

# 3. 마이그레이션 확인
sudo docker compose -f docker-compose.aws.yml exec web python manage.py showmigrations
```

## 📁 파일 구조

```
/home/ubuntu/hosptal/
├── .env.aws                    # AWS 환경 변수
├── docker-compose.aws.yml      # AWS용 Docker Compose 설정
├── deploy_aws_complete.sh      # 완전 자동 배포 스크립트
├── quick_deploy.sh             # 빠른 업데이트 스크립트
├── Dockerfile                  # Docker 이미지 정의
├── requirements.txt            # Python 패키지
├── manage.py                   # Django 관리 스크립트
├── config/                     # Django 설정
│   ├── settings/
│   │   ├── base.py
│   │   ├── aws.py             # AWS 전용 설정
│   │   └── production.py
│   └── urls.py
└── apps/                       # Django 앱들
```

## 🔐 보안 체크리스트

- [ ] SECRET_KEY 변경 (`.env.aws`)
- [ ] DB_PASSWORD 변경 (`.env.aws`)
- [ ] AWS Security Group 설정 (필요한 포트만 오픈)
- [ ] 슈퍼유저 비밀번호 강력하게 설정
- [ ] DEBUG=False 확인
- [ ] HTTPS 설정 (프로덕션 권장)
- [ ] 정기 백업 설정
- [ ] 로그 모니터링 설정

## 📈 성능 최적화

### Gunicorn Workers 조정

`.env.aws` 또는 `docker-compose.aws.yml`에서:
```yaml
command: gunicorn --bind 0.0.0.0:8000 --workers 4 --timeout 120 config.wsgi:application
```

Workers 수 = (2 × CPU 코어 수) + 1

### 데이터베이스 연결 풀

`config/settings/aws.py`에서:
```python
DATABASES = {
    'default': {
        ...
        'CONN_MAX_AGE': 60,  # 연결 재사용
    }
}
```

## 🔄 백업 및 복구

### 데이터베이스 백업

```bash
# 백업
sudo docker exec hosptal-db pg_dump -U dental_user dental_ai > backup_$(date +%Y%m%d).sql

# 복구
sudo docker exec -i hosptal-db psql -U dental_user dental_ai < backup_20241110.sql
```

### 전체 볼륨 백업

```bash
# 백업
sudo docker run --rm -v hosptal_postgres_data:/data -v $(pwd):/backup ubuntu tar czf /backup/postgres_backup.tar.gz /data

# 복구
sudo docker run --rm -v hosptal_postgres_data:/data -v $(pwd):/backup ubuntu tar xzf /backup/postgres_backup.tar.gz -C /
```

## 📞 지원

문제가 발생하면:
1. 로그 확인: `sudo docker compose -f docker-compose.aws.yml logs -f`
2. 헬스체크: `curl http://localhost:8000/api/health/`
3. 문서 참조: `deploy_aws_manual.md`
4. GitHub Issues

## 📚 추가 문서

- [상세 배포 가이드](deploy_aws_manual.md)
- [개발 가이드](DEVELOPMENT_GUIDE.md)
- [프로덕션 설정](PRODUCTION_SETUP.md)
