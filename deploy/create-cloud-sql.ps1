# Cloud SQL PostgreSQL 인스턴스 생성 스크립트 (PowerShell)

Write-Host "🗄️ Cloud SQL PostgreSQL 인스턴스 생성 중..." -ForegroundColor Green

# 환경 변수 설정
$PROJECT_ID = "dental-ai-2024"
$REGION = "asia-northeast3"
$INSTANCE_NAME = "dental-ai-db"
$DATABASE_NAME = "dental_ai"
$DB_USER = "postgres"

# 랜덤 패스워드 생성
$DB_PASSWORD = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 20 | ForEach-Object {[char]$_})

Write-Host "📋 설정 정보:" -ForegroundColor Blue
Write-Host "  프로젝트: $PROJECT_ID" -ForegroundColor White
Write-Host "  리전: $REGION" -ForegroundColor White
Write-Host "  인스턴스명: $INSTANCE_NAME" -ForegroundColor White
Write-Host "  데이터베이스명: $DATABASE_NAME" -ForegroundColor White
Write-Host "  사용자: $DB_USER" -ForegroundColor White

# Cloud SQL 인스턴스 생성
Write-Host "🚀 Cloud SQL 인스턴스 생성 중... (약 5-10분 소요)" -ForegroundColor Yellow
try {
    gcloud sql instances create $INSTANCE_NAME `
        --database-version=POSTGRES_15 `
        --tier=db-f1-micro `
        --region=$REGION `
        --storage-type=SSD `
        --storage-size=20GB `
        --storage-auto-increase `
        --backup-start-time=03:00 `
        --maintenance-window-day=SUN `
        --maintenance-window-hour=04 `
        --maintenance-release-channel=production `
        --deletion-protection
    
    Write-Host "✅ Cloud SQL 인스턴스 생성 완료!" -ForegroundColor Green
} catch {
    Write-Host "❌ Cloud SQL 인스턴스 생성 실패: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# 데이터베이스 사용자 패스워드 설정
Write-Host "🔐 데이터베이스 사용자 패스워드 설정 중..." -ForegroundColor Blue
try {
    gcloud sql users set-password $DB_USER `
        --instance=$INSTANCE_NAME `
        --password=$DB_PASSWORD
    
    Write-Host "✅ 패스워드 설정 완료!" -ForegroundColor Green
} catch {
    Write-Host "❌ 패스워드 설정 실패: $($_.Exception.Message)" -ForegroundColor Red
}

# 데이터베이스 생성
Write-Host "📊 데이터베이스 생성 중..." -ForegroundColor Blue
try {
    gcloud sql databases create $DATABASE_NAME `
        --instance=$INSTANCE_NAME
    
    Write-Host "✅ 데이터베이스 생성 완료!" -ForegroundColor Green
} catch {
    Write-Host "❌ 데이터베이스 생성 실패: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "📝 연결 정보:" -ForegroundColor Cyan
Write-Host "  인스턴스 연결명: $PROJECT_ID`:$REGION`:$INSTANCE_NAME" -ForegroundColor White
Write-Host "  데이터베이스명: $DATABASE_NAME" -ForegroundColor White
Write-Host "  사용자명: $DB_USER" -ForegroundColor White
Write-Host "  패스워드: $DB_PASSWORD" -ForegroundColor Yellow

$DATABASE_URL = "postgresql://$DB_USER`:$DB_PASSWORD@/$DATABASE_NAME`?host=/cloudsql/$PROJECT_ID`:$REGION`:$INSTANCE_NAME"

Write-Host ""
Write-Host "🔧 Django 설정에 사용할 DATABASE_URL:" -ForegroundColor Cyan
Write-Host $DATABASE_URL -ForegroundColor White

Write-Host ""
Write-Host "⚠️  패스워드를 안전한 곳에 저장하세요!" -ForegroundColor Red

# 환경 변수 파일 업데이트
Write-Host "📄 .env.production 파일 업데이트 중..." -ForegroundColor Blue
try {
    $envContent = Get-Content ".env.production" -Raw
    $envContent = $envContent -replace "DATABASE_URL=.*", "DATABASE_URL=$DATABASE_URL"
    Set-Content ".env.production" $envContent
    
    Write-Host "✅ .env.production 파일 업데이트 완료!" -ForegroundColor Green
} catch {
    Write-Host "❌ 환경 변수 파일 업데이트 실패: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "수동으로 다음 내용을 .env.production 파일에 추가하세요:" -ForegroundColor Yellow
    Write-Host "DATABASE_URL=$DATABASE_URL" -ForegroundColor White
}

Write-Host ""
Write-Host "🎉 모든 설정이 완료되었습니다!" -ForegroundColor Green