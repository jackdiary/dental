# Google Cloud SDK PATH 영구 설정 스크립트

Write-Host "🔧 Google Cloud SDK PATH 설정 중..." -ForegroundColor Green

# Google Cloud SDK 설치 경로
$gcloudPath = "C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"

# 현재 사용자의 PATH 환경 변수 가져오기
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")

# 이미 PATH에 있는지 확인
if ($currentPath -notlike "*$gcloudPath*") {
    Write-Host "📁 PATH에 Google Cloud SDK 경로 추가 중..." -ForegroundColor Yellow
    
    # 새로운 PATH 설정
    $newPath = $currentPath + ";" + $gcloudPath
    
    # 사용자 환경 변수에 설정
    [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
    
    Write-Host "✅ PATH 설정 완료!" -ForegroundColor Green
    Write-Host "⚠️  새 터미널 창을 열어야 적용됩니다." -ForegroundColor Yellow
} else {
    Write-Host "✅ Google Cloud SDK가 이미 PATH에 설정되어 있습니다." -ForegroundColor Green
}

# 현재 세션에서도 PATH 설정
$env:PATH += ";$gcloudPath"

Write-Host "🧪 gcloud 명령어 테스트 중..." -ForegroundColor Blue
try {
    $version = gcloud version --format="value(Google Cloud SDK)"
    Write-Host "✅ Google Cloud SDK 버전: $version" -ForegroundColor Green
} catch {
    Write-Host "❌ gcloud 명령어 실행 실패" -ForegroundColor Red
}

Write-Host "🎉 설정 완료!" -ForegroundColor Green