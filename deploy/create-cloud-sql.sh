#!/bin/bash
# Cloud SQL PostgreSQL 인스턴스 생성 스크립트

set -e

echo "🗄️ Cloud SQL PostgreSQL 인스턴스 생성 중..."

# 환경 변수 설정
PROJECT_ID="dental-ai-2024"
REGION="asia-northeast3"
INSTANCE_NAME="dental-ai-db"
DATABASE_NAME="dental_ai"
DB_USER="postgres"

# 랜덤 패스워드 생성 (실제 운영에서는 더 안전한 방법 사용)
DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)

echo "📋 설정 정보:"
echo "  프로젝트: $PROJECT_ID"
echo "  리전: $REGION"
echo "  인스턴스명: $INSTANCE_NAME"
echo "  데이터베이스명: $DATABASE_NAME"
echo "  사용자: $DB_USER"

# Cloud SQL 인스턴스 생성
echo "🚀 Cloud SQL 인스턴스 생성 중... (약 5-10분 소요)"
gcloud sql instances create $INSTANCE_NAME \
    --database-version=POSTGRES_15 \
    --tier=db-f1-micro \
    --region=$REGION \
    --storage-type=SSD \
    --storage-size=20GB \
    --storage-auto-increase \
    --backup-start-time=03:00 \
    --enable-bin-log \
    --maintenance-window-day=SUN \
    --maintenance-window-hour=04 \
    --maintenance-release-channel=production \
    --deletion-protection

# 데이터베이스 사용자 패스워드 설정
echo "🔐 데이터베이스 사용자 패스워드 설정 중..."
gcloud sql users set-password $DB_USER \
    --instance=$INSTANCE_NAME \
    --password=$DB_PASSWORD

# 데이터베이스 생성
echo "📊 데이터베이스 생성 중..."
gcloud sql databases create $DATABASE_NAME \
    --instance=$INSTANCE_NAME

# Cloud Run에서 접근할 수 있도록 권한 설정
echo "🔗 Cloud Run 연결 설정 중..."
gcloud sql instances patch $INSTANCE_NAME \
    --authorized-networks=0.0.0.0/0 \
    --quiet

echo "✅ Cloud SQL 인스턴스 생성 완료!"
echo ""
echo "📝 연결 정보:"
echo "  인스턴스 연결명: $PROJECT_ID:$REGION:$INSTANCE_NAME"
echo "  데이터베이스명: $DATABASE_NAME"
echo "  사용자명: $DB_USER"
echo "  패스워드: $DB_PASSWORD"
echo ""
echo "🔧 Django 설정에 사용할 DATABASE_URL:"
echo "postgresql://$DB_USER:$DB_PASSWORD@/$DATABASE_NAME?host=/cloudsql/$PROJECT_ID:$REGION:$INSTANCE_NAME"
echo ""
echo "⚠️  패스워드를 안전한 곳에 저장하세요!"

# 환경 변수 파일 업데이트
echo "📄 .env.production 파일 업데이트 중..."
sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@/$DATABASE_NAME?host=/cloudsql/$PROJECT_ID:$REGION:$INSTANCE_NAME|" .env.production

echo "🎉 모든 설정이 완료되었습니다!"