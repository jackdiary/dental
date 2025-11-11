#!/bin/bash

# 가격비교 및 회원가입 수정사항 배포 스크립트

echo "🚀 배포 시작..."

# EC2 서버 정보
EC2_HOST="3.36.129.103"
EC2_USER="ubuntu"
EC2_PATH="/home/ubuntu/hosptal"

echo "📦 수정된 파일들을 EC2로 전송 중..."

# 백엔드 파일 전송
scp apps/accounts/serializers.py ${EC2_USER}@${EC2_HOST}:${EC2_PATH}/apps/accounts/
scp apps/api/price_views.py ${EC2_USER}@${EC2_HOST}:${EC2_PATH}/apps/api/

# 프론트엔드 파일 전송
scp frontend/src/pages/PriceComparisonPage.jsx ${EC2_USER}@${EC2_HOST}:${EC2_PATH}/frontend/src/pages/
scp frontend/src/contexts/AuthContext.jsx ${EC2_USER}@${EC2_HOST}:${EC2_PATH}/frontend/src/contexts/

echo "🔨 EC2 서버에서 빌드 및 재시작 중..."

# EC2에서 명령 실행
ssh ${EC2_USER}@${EC2_HOST} << 'ENDSSH'
cd /home/ubuntu/hosptal

# 프론트엔드 빌드
echo "📦 프론트엔드 빌드 중..."
cd frontend
npm run build
cd ..

# Django static 파일 수집
echo "📦 Django static 파일 수집 중..."
source venv/bin/activate
python manage.py collectstatic --noinput --settings=config.settings.production

# Gunicorn 재시작
echo "🔄 Gunicorn 재시작 중..."
sudo systemctl restart gunicorn

# Nginx 재시작
echo "🔄 Nginx 재시작 중..."
sudo systemctl restart nginx

echo "✅ 배포 완료!"
ENDSSH

echo "✅ 모든 작업이 완료되었습니다!"
