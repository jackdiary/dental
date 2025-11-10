# 최종 수정 가이드

EC2 서버에서 아래 명령어들을 순서대로 실행하세요.

## 1단계: 프론트엔드 빌드
```bash
cd /home/ubuntu/hosptal/frontend && npm run build && cd ..
```

## 2단계: 가격 데이터 생성
```bash
docker exec hosptal-web python -c "
import os, django, random
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()
from apps.clinics.models import Clinic
from apps.analysis.models import PriceData

PRICE_RANGES = {
    'scaling': (50000, 150000),
    'implant': (1000000, 3000000),
    'root_canal': (100000, 500000),
    'orthodontics': (3000000, 8000000),
    'whitening': (200000, 800000),
    'extraction': (50000, 200000),
    'filling': (50000, 300000),
    'crown': (300000, 1000000),
    'bridge': (500000, 2000000),
    'denture': (800000, 3000000),
}

clinics = Clinic.objects.all()
print('치과 수:', clinics.count())

created = 0
for clinic in clinics:
    treatments = random.sample(list(PRICE_RANGES.keys()), random.randint(3, 5))
    for treatment_type in treatments:
        min_price, max_price = PRICE_RANGES[treatment_type]
        price = round(random.randint(min_price, max_price) / 10000) * 10000
        PriceData.objects.create(
            clinic=clinic,
            treatment_type=treatment_type,
            price=price,
            currency='KRW',
            extraction_confidence=0.95,
            extraction_method='manual',
            is_verified=True,
            is_outlier=False
        )
        created += 1

print('생성된 가격 데이터:', created)
"
```

## 3단계: Static 파일 수집 및 재시작
```bash
docker exec hosptal-web python manage.py collectstatic --noinput --settings=config.settings.production
docker restart hosptal-web
```

## 4단계: 확인
```bash
echo "완료! http://3.36.129.103:8000 에서 확인하세요"
```
