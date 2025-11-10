#!/bin/bash
# 백엔드 배포 스크립트

set -e

echo "🚀 백엔드 배포 시작..."

# 환경 변수 설정
PROJECT_ID="dental-ai-2024"
REGION="asia-northeast3"
SERVICE_NAME="dental-ai-backend"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "📦 Docker 이미지 빌드 중..."
docker build -f Dockerfile.backend -t ${IMAGE_NAME}:latest .

echo "📤 이미지를 Container Registry에 푸시 중..."
docker push ${IMAGE_NAME}:latest

echo "🌐 Cloud Run에 배포 중..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 10 \
  --min-instances 0 \
  --concurrency 80 \
  --timeout 300 \
  --add-cloudsql-instances ${PROJECT_ID}:${REGION}:dental-ai-db \
  --set-env-vars "GCP_PROJECT_ID=${PROJECT_ID}" \
  --set-env-vars "GCP_REGION=${REGION}" \
  --set-env-vars "DJANGO_SETTINGS_MODULE=config.settings.production" \
  --set-env-vars "DATABASE_URL=postgresql://dental_user:dental_password_2024@/dental_ai?host=/cloudsql/${PROJECT_ID}:${REGION}:dental-ai-db" \
  --set-env-vars "REDIS_URL=redis://10.252.26.155:6379/0" \
  --set-env-vars "GS_BUCKET_NAME=${PROJECT_ID}-static" \
  --set-env-vars "ALLOWED_HOSTS=*.run.app,${SERVICE_NAME}-*.run.app" \
  --set-env-vars "DEBUG=False"

echo "✅ 백엔드 배포 완료!"

# 배포된 URL 확인
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format="value(status.url)")
echo "🌍 서비스 URL: ${SERVICE_URL}"

# 헬스 체크
echo "🏥 헬스 체크 중..."
curl -f "${SERVICE_URL}/api/health/" || echo "⚠️ 헬스 체크 실패"

echo "🎉 배포 완료!"