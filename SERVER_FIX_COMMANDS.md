# EC2 서버에서 직접 실행할 명령어

## 1단계: 백엔드 수정 (회원가입 문제 해결)

```bash
cd /home/ubuntu/hosptal

# serializers.py 백업
cp apps/accounts/serializers.py apps/accounts/serializers.py.backup

# 파일 수정
cat > /tmp/serializers_patch.py << 'EOF'
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

# 기존 validate 메서드 부분을 새 코드로 교체
sed -i '/def validate(self, attrs):/,/return attrs/c\    def validate(self, attrs):\n        if attrs["password"] != attrs["password_confirm"]:\n            raise serializers.ValidationError({"password": "비밀번호가 일치하지 않습니다."})\n        return attrs\n\n    def validate_email(self, value):\n        if User.objects.filter(email=value).exists():\n            raise serializers.ValidationError("이미 사용 중인 이메일입니다.")\n        return value\n\n    def validate_username(self, value):\n        if User.objects.filter(username=value).exists():\n            raise serializers.ValidationError("이미 사용 중인 사용자명입니다.")\n        return value' apps/accounts/serializers.py
```

## 2단계: 프론트엔드 수정 (가격비교 문제 해결)

```bash
# PriceComparisonPage.jsx 백업
cp frontend/src/pages/PriceComparisonPage.jsx frontend/src/pages/PriceComparisonPage.jsx.backup

# handleSearch 함수 수정
sed -i 's/const response = await priceAPI.getComparison({/const treatmentCode = getTreatmentCode(selectedTreatment);\n      console.log("Searching with:", { district: selectedDistrict, treatment_type: treatmentCode });\n      \n      const response = await priceAPI.getComparison({/' frontend/src/pages/PriceComparisonPage.jsx

sed -i 's/treatment_type: selectedTreatment/treatment_type: treatmentCode/' frontend/src/pages/PriceComparisonPage.jsx
```

## 3단계: 빌드 및 배포

```bash
# 프론트엔드 빌드
cd frontend
npm run build
cd ..

# Static 파일 수집
source venv/bin/activate
python manage.py collectstatic --noinput --settings=config.settings.production

# 서비스 재시작
sudo systemctl restart gunicorn
sudo systemctl restart nginx

# 상태 확인
sudo systemctl status gunicorn
sudo systemctl status nginx
```

## 더 간단한 방법: 한 번에 실행

```bash
cd /home/ubuntu/hosptal && \
cp apps/accounts/serializers.py apps/accounts/serializers.py.backup && \
cp frontend/src/pages/PriceComparisonPage.jsx frontend/src/pages/PriceComparisonPage.jsx.backup && \
cd frontend && npm run build && cd .. && \
source venv/bin/activate && \
python manage.py collectstatic --noinput --settings=config.settings.production && \
sudo systemctl restart gunicorn && \
sudo systemctl restart nginx && \
echo "✅ 완료!"
```

## 문제 발생 시 롤백

```bash
# 백업 파일로 복구
cp apps/accounts/serializers.py.backup apps/accounts/serializers.py
cp frontend/src/pages/PriceComparisonPage.jsx.backup frontend/src/pages/PriceComparisonPage.jsx

# 다시 빌드
cd frontend && npm run build && cd ..
source venv/bin/activate
python manage.py collectstatic --noinput --settings=config.settings.production
sudo systemctl restart gunicorn
sudo systemctl restart nginx
```
