# AWS EC2 배포 가이드 (완전 자동화)

## 🚀 빠른 시작

### 1단계: 서버에 프로젝트 클론

```bash
cd /home/ubuntu/hosptal
git clone https://github.com/jackdiary/dental.git .
```

### 2단계: 배포 스크립트 실행

```bash
chmod +x deploy_aws_complete.sh
./deploy_aws_complete.sh
```

끝! 이제 `http://3.36.129.103:8000`으로 접속하세요.

---

# AWS EC2 수동 배포 가이드 (상세)

## 1. 서버 접속
```bash
ssh -i den.pem ubuntu@3.36.129.103
```

## 2. 현재 상태 확인
```bash
# 실행 중인 프로세스 확인
ps aux | grep python
ps aux | grep gunicorn

# 포트 확인
sudo netstat -tulpn | grep :8000
sudo netstat -tulpn | grep :80

# 로그 확인
tail -f /home/ubuntu/dental-ai/logs/gunicorn-error.log
sudo tail -f /var/log/nginx/error.log
```

## 3. 긴급 수정 (400 Bad Request 해결)

### A) Django 설정 수정
```bash
cd /home/ubuntu/dental-ai
source venv/bin/activate

# ALLOWED_HOSTS 확인
python manage.py shell
>>> from django.conf import settings
>>> print(settings.ALLOWED_HOSTS)
>>> exit()
```

### B) 환경 변수 설정
```bash
export DJANGO_SETTINGS_MODULE=config.settings.aws
export ALLOWED_HOSTS="3.36.129.103,localhost,127.0.0.1"
```

### C) Gunicorn 재시작
```bash
# 기존 프로세스 종료
pkill gunicorn

# Gunicorn 직접 실행 (테스트)
gunicorn --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --env DJANGO_SETTINGS_MODULE=config.settings.aws \
    config.wsgi:application

# 또는 서비스로 재시작
sudo systemctl restart gunicorn
sudo systemctl status gunicorn
```

### D) Nginx 설정 확인
```bash
# Nginx 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
sudo systemctl status nginx
```

## 4. 프론트엔드 빌드 및 배포

### 로컬에서 빌드
```bash
cd frontend
npm install
npm run build
```

### 서버로 업로드
```bash
scp -i den.pem -r frontend/dist ubuntu@3.36.129.103:/home/ubuntu/dental-ai/frontend/
```

### 또는 서버에서 직접 빌드
```bash
ssh -i den.pem ubuntu@3.36.129.103

# Node.js 설치 (없는 경우)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

cd /home/ubuntu/dental-ai/frontend
npm install
npm run build
```

## 5. 데이터베이스 마이그레이션
```bash
cd /home/ubuntu/dental-ai
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=config.settings.aws

python manage.py migrate
python manage.py collectstatic --noinput
```

## 6. 대량 데이터 업로드

### SQL 파일 업로드
```bash
scp -i den.pem complete_database_insert.sql ubuntu@3.36.129.103:~/
```

### 서버에서 실행
```bash
ssh -i den.pem ubuntu@3.36.129.103
cd /home/ubuntu/dental-ai
source venv/bin/activate

# SQLite에 데이터 삽입
sqlite3 db.sqlite3 < ~/complete_database_insert.sql
```

## 7. 방화벽 설정 (AWS Security Group)

AWS 콘솔에서 다음 포트 열기:
- **80** (HTTP) - 0.0.0.0/0
- **8000** (Django) - 0.0.0.0/0 (테스트용, 나중에 제거)
- **22** (SSH) - 본인 IP만

## 8. 문제 해결

### 400 Bad Request
```python
# config/settings/aws.py 확인
ALLOWED_HOSTS = ['3.36.129.103', 'localhost', '127.0.0.1']
```

### CORS 오류
```python
# config/settings/aws.py 확인
CORS_ALLOW_ALL_ORIGINS = True
SECURE_CROSS_ORIGIN_OPENER_POLICY = None
```

### 프론트엔드 안 뜸
```bash
# Nginx 설정 확인
sudo nginx -t
sudo systemctl restart nginx

# 프론트엔드 파일 확인
ls -la /home/ubuntu/dental-ai/frontend/dist/
```

## 9. 서비스 상태 확인
```bash
# 모든 서비스 상태
sudo systemctl status gunicorn
sudo systemctl status nginx

# 로그 실시간 확인
tail -f /home/ubuntu/dental-ai/logs/gunicorn-error.log
sudo tail -f /var/log/nginx/error.log
```

## 10. 빠른 재시작
```bash
sudo systemctl restart gunicorn nginx
```

## 접속 테스트
- 프론트엔드: http://3.36.129.103
- 백엔드 API: http://3.36.129.103/api/
- 관리자: http://3.36.129.103/admin/


## 📋 수동 배포 단계

### 1. 환경 변수 설정

`.env.aws` 파일이 자동으로 생성되어 있습니다. 필요시 수정:

```bash
nano .env.aws
```

주요 설정:
- `SECRET_KEY`: 프로덕션용 시크릿 키 (변경 권장)
- `DB_PASSWORD`: 데이터베이스 비밀번호 (변경 권장)
- `ALLOWED_HOSTS`: 서버 IP 주소
- `CORS_ALLOWED_ORIGINS`: 허용할 프론트엔드 도메인

### 2. Docker Compose로 배포

```bash
# 기존 컨테이너 중지
sudo docker compose -f docker-compose.aws.yml down

# 이미지 빌드
sudo docker compose -f docker-compose.aws.yml build

# 서비스 시작
sudo docker compose -f docker-compose.aws.yml up -d

# 마이그레이션
sudo docker compose -f docker-compose.aws.yml exec web python manage.py migrate

# 정적 파일 수집
sudo docker compose -f docker-compose.aws.yml exec web python manage.py collectstatic --noinput

# 슈퍼유저 생성
sudo docker compose -f docker-compose.aws.yml exec web python manage.py createsuperuser
```

### 3. 서비스 확인

```bash
# 컨테이너 상태 확인
sudo docker compose -f docker-compose.aws.yml ps

# 로그 확인
sudo docker compose -f docker-compose.aws.yml logs -f web

# 헬스체크
curl http://localhost:8000/api/health/
```

## 🔧 유용한 명령어

### 로그 확인
```bash
# 웹 서비스 로그
sudo docker compose -f docker-compose.aws.yml logs -f web

# 모든 서비스 로그
sudo docker compose -f docker-compose.aws.yml logs -f

# 최근 100줄만 보기
sudo docker compose -f docker-compose.aws.yml logs --tail=100 web
```

### 서비스 관리
```bash
# 서비스 재시작
sudo docker compose -f docker-compose.aws.yml restart web

# 특정 서비스만 재시작
sudo docker compose -f docker-compose.aws.yml restart celery

# 서비스 중지
sudo docker compose -f docker-compose.aws.yml stop

# 서비스 시작
sudo docker compose -f docker-compose.aws.yml start

# 완전 종료 (볼륨 포함)
sudo docker compose -f docker-compose.aws.yml down -v
```

### 컨테이너 접속
```bash
# 웹 컨테이너 접속
sudo docker exec -it hosptal-web bash

# 데이터베이스 컨테이너 접속
sudo docker exec -it hosptal-db psql -U dental_user -d dental_ai

# Redis 컨테이너 접속
sudo docker exec -it hosptal-redis redis-cli
```

### Django 관리 명령어
```bash
# 마이그레이션 생성
sudo docker compose -f docker-compose.aws.yml exec web python manage.py makemigrations

# 마이그레이션 적용
sudo docker compose -f docker-compose.aws.yml exec web python manage.py migrate

# Django 쉘
sudo docker compose -f docker-compose.aws.yml exec web python manage.py shell

# 데이터베이스 초기화 (주의!)
sudo docker compose -f docker-compose.aws.yml exec web python manage.py flush
```

## 🐛 문제 해결

### 500 Internal Server Error

1. 로그 확인:
```bash
sudo docker compose -f docker-compose.aws.yml logs web
```

2. 데이터베이스 연결 확인:
```bash
sudo docker compose -f docker-compose.aws.yml exec web python manage.py dbshell
```

3. 환경 변수 확인:
```bash
sudo docker compose -f docker-compose.aws.yml exec web env | grep DJANGO
```

### 400 Bad Request

`ALLOWED_HOSTS` 설정 확인:
```bash
# .env.aws 파일 수정
nano .env.aws

# ALLOWED_HOSTS에 서버 IP 추가
ALLOWED_HOSTS=3.36.129.103,localhost,127.0.0.1

# 서비스 재시작
sudo docker compose -f docker-compose.aws.yml restart web
```

### CORS 에러

`.env.aws`에서 CORS 설정 확인:
```bash
CORS_ALLOWED_ORIGINS=http://3.36.129.103:3000,http://3.36.129.103
```

### 데이터베이스 연결 실패

1. PostgreSQL 컨테이너 상태 확인:
```bash
sudo docker compose -f docker-compose.aws.yml ps db
```

2. 데이터베이스 로그 확인:
```bash
sudo docker compose -f docker-compose.aws.yml logs db
```

3. 데이터베이스 재시작:
```bash
sudo docker compose -f docker-compose.aws.yml restart db
```

## 📊 모니터링

### 헬스체크 엔드포인트

- 전체 헬스체크: `http://3.36.129.103:8000/api/health/`
- 준비 상태: `http://3.36.129.103:8000/api/ready/`
- 생존 확인: `http://3.36.129.103:8000/api/alive/`

### 리소스 사용량 확인

```bash
# Docker 컨테이너 리소스 사용량
sudo docker stats

# 디스크 사용량
df -h

# 메모리 사용량
free -h

# CPU 사용량
top
```

## 🔄 업데이트 배포

코드 변경 후 재배포:

```bash
# 1. 최신 코드 가져오기
git pull origin main

# 2. 컨테이너 재빌드 및 재시작
sudo docker compose -f docker-compose.aws.yml up -d --build

# 3. 마이그레이션 (필요시)
sudo docker compose -f docker-compose.aws.yml exec web python manage.py migrate

# 4. 정적 파일 수집 (필요시)
sudo docker compose -f docker-compose.aws.yml exec web python manage.py collectstatic --noinput
```

## 🔐 보안 권장사항

1. **SECRET_KEY 변경**: `.env.aws`의 SECRET_KEY를 강력한 랜덤 문자열로 변경
2. **데이터베이스 비밀번호 변경**: DB_PASSWORD를 강력한 비밀번호로 변경
3. **방화벽 설정**: AWS Security Group에서 필요한 포트만 열기
4. **HTTPS 설정**: 프로덕션에서는 HTTPS 사용 권장 (Let's Encrypt + Nginx)
5. **정기 백업**: 데이터베이스 정기 백업 설정

## 📞 지원

문제가 발생하면:
1. 로그 확인
2. GitHub Issues에 문의
3. 문서 참조: `/docs` 디렉토리
