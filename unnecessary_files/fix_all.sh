#!/bin/bash

# 한 번에 모든 문제 해결하는 스크립트
# 로컬에서 실행: bash fix_all.sh

echo "🚀 수정 및 배포 시작..."

EC2_USER="ubuntu"
EC2_HOST="3.36.129.103"

# 1. 로컬에서 프론트엔드 빌드
echo "📦 로컬에서 프론트엔드 빌드 중..."
cd frontend
npm run build
cd ..

# 2. 빌드된 파일과 수정된 백엔드 파일을 서버로 전송
echo "📤 파일 전송 중..."
scp -r frontend/dist ${EC2_USER}@${EC2_HOST}:/home/ubuntu/hosptal/frontend/
scp apps/accounts/serializers.py ${EC2_USER}@${EC2_HOST}:/home/ubuntu/hosptal/apps/accounts/

# 3. 서버에서 재시작
echo "🔄 서버 재시작 중..."
ssh ${EC2_USER}@${EC2_HOST} << 'ENDSSH'
cd /home/ubuntu/hosptal
source venv/bin/activate
python manage.py collectstatic --noinput --settings=config.settings.production
sudo systemctl restart gunicorn
sudo systemctl restart nginx
echo "✅ 완료!"
ENDSSH

echo "✅ 모든 작업 완료!"
echo "🌐 http://3.36.129.103:8000 에서 확인하세요"
