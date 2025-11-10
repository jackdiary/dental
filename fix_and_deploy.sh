#!/bin/bash
set -e

echo "🔧 AWS 배포 문제 해결 및 데이터 적용 시작..."

# 1. 모든 컨테이너 중지 및 볼륨 삭제
echo "📋 1. 기존 컨테이너 및 볼륨 정리..."
cd /home/ubuntu/hosptal
sudo docker compose -f docker-compose.aws.yml down -v

# 2. 최신 코드 가져오기
echo "📋 2. 최신 코드 가져오기..."
git pull origin main

# 3. 데이터베이스 시작
echo "📋 3. 데이터베이스 시작..."
sudo docker compose -f docker-compose.aws.yml up -d db

# 4. 데이터베이스 준비 대기
echo "⏳ 데이터베이스 준비 중..."
sleep 15

# 5. Redis 시작
echo "📋 4. Redis 시작..."
sudo docker compose -f docker-compose.aws.yml up -d redis
sleep 5

# 6. 웹 서비스 빌드 및 시작
echo "📋 5. 웹 서비스 빌드 및 시작..."
sudo docker compose -f docker-compose.aws.yml build web
sudo docker compose -f docker-compose.aws.yml up -d web

# 7. 마이그레이션 대기
echo "⏳ 마이그레이션 대기 중..."
sleep 20

# 8. 마이그레이션 상태 확인
echo "📋 6. 마이그레이션 상태 확인..."
sudo docker compose -f docker-compose.aws.yml logs web | tail -50

# 9. 데이터 적용
echo "📋 7. 대량 데이터 적용 중..."
sudo docker exec -i hosptal-db psql -U postgres -d postgres < /home/ubuntu/hosptal/complete_database_insert.sql

# 10. Celery 서비스 시작
echo "📋 8. Celery 서비스 시작..."
sudo docker compose -f docker-compose.aws.yml up -d celery celery-beat

# 11. 모든 서비스 상태 확인
echo "📋 9. 서비스 상태 확인..."
sudo docker compose -f docker-compose.aws.yml ps

# 12. 웹 서비스 로그 확인
echo "📋 10. 웹 서비스 로그..."
sudo docker compose -f docker-compose.aws.yml logs web | tail -30

echo ""
echo "✅ 배포 완료!"
echo "🌐 서비스 접속: http://3.36.129.103:8000"
echo ""
echo "📊 유용한 명령어:"
echo "  - 로그 확인: sudo docker compose -f docker-compose.aws.yml logs -f web"
echo "  - 서비스 재시작: sudo docker compose -f docker-compose.aws.yml restart web"
echo "  - 데이터 확인: sudo docker exec -it hosptal-db psql -U postgres -d postgres -c 'SELECT COUNT(*) FROM clinics_clinic;'"
