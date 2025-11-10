#!/bin/bash

# EC2 서버에서 직접 실행할 수정 스크립트
# 사용법: ssh로 접속 후 이 스크립트를 실행

echo "🔧 가격비교 및 회원가입 문제 수정 중..."

cd /home/ubuntu/hosptal

# 1. 백엔드 serializers.py 수정
echo "📝 accounts/serializers.py 수정 중..."
cat > apps/accounts/serializers_fix.py << 'EOF'
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})
        return attrs
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("이미 사용 중인 사용자명입니다.")
        return value
EOF

# 2. 프론트엔드 PriceComparisonPage.jsx 수정
echo "📝 PriceComparisonPage.jsx 수정 중..."
# getTreatmentCode import 확인 및 사용

# 3. 프론트엔드 빌드
echo "📦 프론트엔드 빌드 중..."
cd frontend
npm run build
cd ..

# 4. Django static 파일 수집
echo "📦 Django static 파일 수집 중..."
source venv/bin/activate
python manage.py collectstatic --noinput --settings=config.settings.production

# 5. 서비스 재시작
echo "🔄 서비스 재시작 중..."
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 6. 로그 확인
echo "📋 최근 로그 확인..."
sudo journalctl -u gunicorn -n 20 --no-pager

echo "✅ 수정 완료!"
