#!/bin/bash
# AWS EC2 배포 스크립트

set -e

echo "🚀 AWS EC2 배포 시작..."

# 변수 설정
EC2_IP="3.36.129.103"
PEM_KEY="den.pem"
EC2_USER="ubuntu"
PROJECT_NAME="dental-ai"
REMOTE_DIR="/home/$EC2_USER/$PROJECT_NAME"

echo "📦 프로젝트 파일 압축 중..."
tar -czf deploy.tar.gz \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='.git' \
    --exclude='*.pyc' \
    --exclude='*.log' \
    --exclude='db.sqlite3' \
    --exclude='staticfiles' \
    --exclude='media' \
    --exclude='*.pem' \
    .

echo "📤 파일 업로드 중..."
scp -i $PEM_KEY deploy.tar.gz $EC2_USER@$EC2_IP:~

echo "🔧 서버에서 배포 실행 중..."
ssh -i $PEM_KEY $EC2_USER@$EC2_IP << 'ENDSSH'
    set -e
    
    PROJECT_NAME="dental-ai"
    REMOTE_DIR="/home/ubuntu/$PROJECT_NAME"
    
    echo "📁 프로젝트 디렉토리 준비..."
    mkdir -p $REMOTE_DIR
    cd $REMOTE_DIR
    
    echo "📦 파일 압축 해제..."
    tar -xzf ~/deploy.tar.gz -C $REMOTE_DIR
    rm ~/deploy.tar.gz
    
    echo "🐍 Python 가상환경 설정..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    
    echo "📚 Python 패키지 설치..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    echo "🗄️ 데이터베이스 마이그레이션..."
    export DJANGO_SETTINGS_MODULE=config.settings.aws
    python manage.py migrate
    
    echo "📦 정적 파일 수집..."
    python manage.py collectstatic --noinput
    
    echo "🔄 Gunicorn 재시작..."
    sudo systemctl restart gunicorn || echo "Gunicorn 서비스가 없습니다. 수동으로 시작해주세요."
    
    echo "🔄 Nginx 재시작..."
    sudo systemctl restart nginx || echo "Nginx 서비스가 없습니다."
    
    echo "✅ 배포 완료!"
ENDSSH

echo "🧹 로컬 임시 파일 정리..."
rm deploy.tar.gz

echo "✅ AWS EC2 배포 완료!"
echo "🌐 접속 주소: http://$EC2_IP"
