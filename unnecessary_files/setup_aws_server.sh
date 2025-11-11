#!/bin/bash
# AWS EC2 서버 초기 설정 스크립트

set -e

EC2_IP="3.36.129.103"
PEM_KEY="den.pem"
EC2_USER="ubuntu"

echo "🔧 AWS EC2 서버 초기 설정 시작..."

ssh -i $PEM_KEY $EC2_USER@$EC2_IP << 'ENDSSH'
    set -e
    
    echo "📦 시스템 패키지 업데이트..."
    sudo apt-get update
    sudo apt-get upgrade -y
    
    echo "🐍 Python 및 필수 패키지 설치..."
    sudo apt-get install -y python3 python3-pip python3-venv
    sudo apt-get install -y nginx
    sudo apt-get install -y git
    
    echo "📁 프로젝트 디렉토리 생성..."
    mkdir -p /home/ubuntu/dental-ai
    mkdir -p /home/ubuntu/dental-ai/logs
    
    echo "🔧 Gunicorn 서비스 설정..."
    sudo tee /etc/systemd/system/gunicorn.service > /dev/null << 'EOF'
[Unit]
Description=Gunicorn daemon for Dental AI
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/dental-ai
Environment="DJANGO_SETTINGS_MODULE=config.settings.aws"
ExecStart=/home/ubuntu/dental-ai/venv/bin/gunicorn \
    --workers 3 \
    --bind 0.0.0.0:8000 \
    --timeout 120 \
    --access-logfile /home/ubuntu/dental-ai/logs/gunicorn-access.log \
    --error-logfile /home/ubuntu/dental-ai/logs/gunicorn-error.log \
    config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF
    
    echo "🌐 Nginx 설정..."
    sudo tee /etc/nginx/sites-available/dental-ai > /dev/null << 'EOF'
server {
    listen 80;
    server_name 3.36.129.103;
    
    client_max_body_size 100M;
    
    # 프론트엔드 정적 파일
    location / {
        root /home/ubuntu/dental-ai/frontend/dist;
        try_files $uri $uri/ /index.html;
        
        # CORS 헤더
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
    }
    
    # 백엔드 API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS 헤더
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "Content-Type, Authorization";
        
        if ($request_method = OPTIONS) {
            return 204;
        }
    }
    
    # Django 정적 파일
    location /static/ {
        alias /home/ubuntu/dental-ai/staticfiles/;
    }
    
    # 미디어 파일
    location /media/ {
        alias /home/ubuntu/dental-ai/media/;
    }
}
EOF
    
    echo "🔗 Nginx 사이트 활성화..."
    sudo ln -sf /etc/nginx/sites-available/dental-ai /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    
    echo "🔄 서비스 시작..."
    sudo systemctl daemon-reload
    sudo systemctl enable gunicorn
    sudo systemctl enable nginx
    
    echo "✅ 서버 초기 설정 완료!"
ENDSSH

echo "✅ AWS EC2 서버 설정 완료!"
echo "다음 단계: ./deploy_aws.sh 실행"
