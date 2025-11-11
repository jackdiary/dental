#!/bin/bash

# 빠른 배포 스크립트 (기존 설정 유지)
# 사용법: ./quick_deploy.sh

set -e

echo "🚀 빠른 배포 시작..."

# 최신 코드 가져오기
echo "📥 최신 코드 가져오기..."
git pull origin main

# 컨테이너 재빌드 및 재시작
echo "🔄 컨테이너 재시작..."
sudo docker compose -f docker-compose.aws.yml up -d --build

# 마이그레이션
echo "🗄️  데이터베이스 마이그레이션..."
sudo docker compose -f docker-compose.aws.yml exec -T web python manage.py migrate

# 정적 파일 수집
echo "📦 정적 파일 수집..."
sudo docker compose -f docker-compose.aws.yml exec -T web python manage.py collectstatic --noinput

# 서비스 상태 확인
echo "✅ 서비스 상태 확인..."
sudo docker compose -f docker-compose.aws.yml ps

echo ""
echo "🎉 배포 완료!"
echo "📍 서비스: http://3.36.129.103:8000"
echo ""
