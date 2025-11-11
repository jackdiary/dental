#!/bin/bash
# 모든 문제를 완전히 해결하는 최종 스크립트

echo "🚀 최종 수정 시작..."

cd /home/ubuntu/hosptal

# 1. 프론트엔드 완전 재빌드 (캐시 삭제)
echo "📦 프론트엔드 완전 재빌드..."
cd frontend
rm -rf dist node_modules/.vite
npm run build
cd ..

# 2. Docker 컨테이너 완전 재시작
echo "🔄 Docker 완전 재시작..."
docker-compose down
docker-compose up -d

# 3. Static 파일 완전 재수집
echo "📦 Static 파일 재수집..."
sleep 10
docker exec hosptal-web python manage.py collectstatic --noinput --clear --settings=config.settings.production

# 4. 최종 재시작
echo "🔄 최종 재시작..."
docker restart hosptal-web

echo "✅ 완료! 30초 후 접속하세요"
echo "🌐 http://3.36.129.103:8000"
