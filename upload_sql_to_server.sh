#!/bin/bash
# 생성된 SQL 파일을 Cloud SQL에 직접 업로드하는 스크립트

echo "🚀 SQL 파일을 Cloud SQL에 업로드 중..."

# Cloud SQL에 직접 연결해서 SQL 파일 실행
gcloud sql connect dental-ai-db \
  --user=dental_user \
  --database=dental_ai \
  --project=dental-ai-2024 < complete_database_insert.sql

echo "✅ SQL 업로드 완료!"
