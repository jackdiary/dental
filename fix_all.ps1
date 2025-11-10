# Windows PowerShell 스크립트 - 한 번에 모든 문제 해결

Write-Host "🚀 수정 및 배포 시작..." -ForegroundColor Green

$EC2_USER = "ubuntu"
$EC2_HOST = "3.36.129.103"

# 1. 로컬에서 프론트엔드 빌드
Write-Host "📦 프론트엔드 빌드 중..." -ForegroundColor Yellow
cd frontend
npm run build
cd ..

# 2. 파일 전송
Write-Host "📤 파일 전송 중..." -ForegroundColor Yellow
scp -r frontend/dist ${EC2_USER}@${EC2_HOST}:/home/ubuntu/hosptal/frontend/
scp apps/accounts/serializers.py ${EC2_USER}@${EC2_HOST}:/home/ubuntu/hosptal/apps/accounts/

# 3. 서버 재시작
Write-Host "🔄 서버 재시작 중..." -ForegroundColor Yellow
ssh ${EC2_USER}@${EC2_HOST} "cd /home/ubuntu/hosptal && source venv/bin/activate && python manage.py collectstatic --noinput --settings=config.settings.production && sudo systemctl restart gunicorn && sudo systemctl restart nginx"

Write-Host "✅ 모든 작업 완료!" -ForegroundColor Green
Write-Host "🌐 http://3.36.129.103:8000 에서 확인하세요" -ForegroundColor Cyan
