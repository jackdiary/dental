#!/usr/bin/env bash
# AWS EC2 배포 스크립트 (docker-compose 기반)
# 프런트 빌드 → 백엔드 이미지 빌드 → collectstatic → migrate → Gunicorn 순서를 강제한다.

set -euo pipefail

export DJANGO_SETTINGS_MODULE="config.settings.aws"

PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu/hosptal}"
COMPOSE_BIN="sudo docker compose -f docker-compose.aws.yml"

echo "🚀 AWS EC2 배포 시작 - 프로젝트 디렉터리: ${PROJECT_DIR}"
cd "${PROJECT_DIR}"

echo "[1/7] 최신 main 브랜치 동기화"
git fetch origin main
git reset --hard origin/main

echo "[2/7] 프런트엔드 포함 백엔드 이미지 빌드"
${COMPOSE_BIN} build web

echo "[3/7] 웹 컨테이너 재기동 (Gunicorn 포함)"
${COMPOSE_BIN} up -d web

echo "[4/7] 정적/미디어 경로 준비"
${COMPOSE_BIN} exec web mkdir -p /app/static /app/staticfiles /app/media

echo "[5/7] 정적 파일 수집 (collectstatic)"
${COMPOSE_BIN} exec -e DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} web \
  python manage.py collectstatic --noinput

echo "[6/7] 데이터베이스 마이그레이션"
${COMPOSE_BIN} exec -e DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE} web \
  python manage.py migrate --noinput

echo "[7/7] 내부 헬스 체크"
${COMPOSE_BIN} exec web curl -f http://localhost:8000/api/health/

echo "✅ 배포 완료! 필요한 경우 'sudo docker compose -f docker-compose.aws.yml logs -f web'로 로그를 확인하세요."
