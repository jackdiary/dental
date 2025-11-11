# 개발자 가이드 - 추가 구현 필요 사항

## 🎯 현재 구현 상태

### ✅ 완료된 기능
- Django 5.0 프로젝트 구조 및 설정
- 사용자 인증 시스템 (JWT)
- 데이터베이스 모델 (Clinic, Review, Analysis 등)
- 크롤링 시스템 기본 구조
- 텍스트 전처리 파이프라인
- REST API 기본 구조
- Docker 컨테이너화

### ⚠️ 추가 구현 필요 사항

## 1. 🤖 머신러닝 모델 구현

### 1.1 감성 분석 모델
현재 인터페이스만 구현되어 있으며, 실제 모델 구현이 필요합니다.

```python
# utils/ml/sentiment_analyzer.py 생성 필요
class ABSASentimentAnalyzer:
    def __init__(self):
        # 실제 모델 로드 구현 필요
        self.models = {
            'price': None,      # 가격 관련 감성 분석 모델
            'skill': None,      # 실력 관련 감성 분석 모델
            'kindness': None,   # 친절도 관련 감성 분석 모델
            'waiting': None,    # 대기시간 관련 감성 분석 모델
            'facility': None,   # 시설 관련 감성 분석 모델
            'overtreatment': None  # 과잉진료 관련 감성 분석 모델
        }
    
    def analyze_aspects(self, text: str) -> Dict[str, float]:
        """6가지 측면별 감성 분석 구현 필요"""
        # TODO: 실제 모델 추론 로직 구현
        pass
```

**구현 방법:**
1. **데이터 수집**: 치과 리뷰 데이터셋 구축 (라벨링 필요)
2. **모델 훈련**: SVM, KoBERT 등을 사용한 측면별 감성 분석 모델 훈련
3. **모델 저장**: 훈련된 모델을 `ml_models/` 디렉토리에 저장
4. **추론 구현**: 실시간 감성 분석 로직 구현

### 1.2 가격 추출 모델
정규식 기반 구현은 완료되었으나, NER 모델 구현이 필요합니다.

```python
# utils/ml/price_extractor.py 구현 필요
class NERPriceExtractor:
    def extract_prices(self, text: str) -> List[Dict]:
        """NER 모델을 사용한 가격 추출"""
        # TODO: NER 모델 구현
        pass
```

## 2. 🕷️ 크롤링 시스템 완성

### 2.1 실제 크롤링 로직
현재 크롤러 구조는 완성되었으나, 실제 웹사이트 크롤링 로직 구현이 필요합니다.

**네이버 플레이스 크롤러 완성:**
```python
# apps/reviews/crawlers/naver.py 수정 필요
def _extract_reviews_from_current_page(self) -> List[ReviewData]:
    """실제 네이버 플레이스 HTML 파싱 로직 구현"""
    # TODO: 실제 네이버 플레이스 DOM 구조에 맞춰 구현
    pass
```

**구글 맵 크롤러 완성:**
```python
# apps/reviews/crawlers/google.py 수정 필요
def _parse_review_element(self, element) -> Optional[ReviewData]:
    """실제 구글 맵 HTML 파싱 로직 구현"""
    # TODO: 실제 구글 맵 DOM 구조에 맞춰 구현
    pass
```

### 2.2 크롤링 안정성 개선
- **IP 차단 방지**: 프록시 로테이션, User-Agent 변경
- **CAPTCHA 처리**: 자동 CAPTCHA 해결 또는 수동 처리 플로우
- **속도 제한**: 사이트별 적절한 지연 시간 설정

## 3. 🧠 추천 알고리즘 구현

### 3.1 종합 점수 계산
현재 모델 구조만 있으며, 실제 계산 로직 구현이 필요합니다.

```python
# apps/recommendations/services.py 생성 필요
class RecommendationEngine:
    def calculate_comprehensive_score(self, clinic_id: int) -> float:
        """
        종합 점수 계산 로직 구현 필요
        - 가격합리성 (30%)
        - 의료진실력 (25%) 
        - 과잉진료역수 (25%)
        - 환자만족도 (20%)
        """
        # TODO: 실제 점수 계산 로직 구현
        pass
    
    def generate_recommendations(self, district: str, treatment_type: str = None) -> List[Dict]:
        """추천 로직 구현 필요"""
        # TODO: 필터링 및 순위 계산 로직 구현
        pass
```

### 3.2 추천 이유 생성
```python
def generate_recommendation_reason(self, clinic: Clinic, scores: Dict) -> str:
    """추천 이유 자동 생성 로직 구현 필요"""
    # TODO: 점수 기반 추천 이유 텍스트 생성
    pass
```

## 4. 📊 통계 및 분석 시스템

### 4.1 지역별 가격 통계
```python
# apps/analysis/services.py 생성 필요
class PriceAnalysisService:
    def calculate_regional_stats(self, district: str, treatment_type: str):
        """지역별 가격 통계 계산"""
        # TODO: 통계 계산 로직 구현
        pass
    
    def detect_price_outliers(self, clinic_id: int):
        """가격 이상치 탐지"""
        # TODO: 이상치 탐지 알고리즘 구현
        pass
```

### 4.2 성능 모니터링
```python
# apps/monitoring/services.py 생성 필요
class PerformanceMonitor:
    def track_api_performance(self):
        """API 성능 추적"""
        pass
    
    def monitor_ml_model_accuracy(self):
        """ML 모델 정확도 모니터링"""
        pass
```

## 5. 🔧 Celery 태스크 완성

### 5.1 분석 태스크 구현
```python
# tasks/analysis.py 수정 필요
@shared_task(bind=True)
def analyze_review_sentiment(self, review_id):
    """실제 감성 분석 로직 구현"""
    try:
        review = Review.objects.get(id=review_id)
        
        # TODO: 실제 감성 분석 모델 호출
        # analyzer = ABSASentimentAnalyzer()
        # scores = analyzer.analyze_aspects(review.original_text)
        
        # TODO: 결과 저장
        # SentimentAnalysis.objects.create(...)
        
        return {'status': 'success', 'review_id': review_id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=30, max_retries=3)
```

### 5.2 주기적 태스크 설정
```python
# config/celery.py에 추가
from celery.schedules import crontab

app.conf.beat_schedule = {
    'update-clinic-scores': {
        'task': 'tasks.analysis.update_all_clinic_scores',
        'schedule': crontab(hour=2, minute=0),  # 매일 새벽 2시
    },
    'cleanup-old-logs': {
        'task': 'tasks.maintenance.cleanup_old_logs',
        'schedule': crontab(hour=3, minute=0),  # 매일 새벽 3시
    },
}
```

## 6. 🌐 API 엔드포인트 완성

### 6.1 추천 API 구현
```python
# apps/api/views.py 생성 필요
class RecommendationAPIView(APIView):
    def post(self, request):
        """치과 추천 API 구현"""
        district = request.data.get('district')
        treatment_type = request.data.get('treatment_type')
        
        # TODO: 추천 로직 호출
        # recommendations = RecommendationEngine().generate_recommendations(...)
        
        return Response({
            'recommendations': [],  # TODO: 실제 추천 결과
            'total_count': 0,
            'district': district
        })
```

### 6.2 가격 비교 API
```python
class PriceComparisonAPIView(APIView):
    def get(self, request):
        """가격 비교 API 구현"""
        # TODO: 지역별, 치료별 가격 비교 데이터 반환
        pass
```

## 7. 🎨 프론트엔드 (선택사항)

현재 백엔드 API만 구현되어 있으며, 프론트엔드 구현이 필요합니다.

### 7.1 기본 웹 인터페이스
- **React/Vue.js**: 사용자 친화적인 웹 인터페이스
- **검색 기능**: 지역별, 치료별 치과 검색
- **추천 결과 표시**: 점수 및 이유와 함께 추천 결과 표시
- **가격 비교**: 시각적 가격 비교 차트

### 7.2 관리자 대시보드
- **크롤링 모니터링**: 실시간 크롤링 상태 확인
- **데이터 관리**: 리뷰 승인/거부, 치과 정보 수정
- **통계 대시보드**: 시스템 사용 통계 및 성능 지표

## 8. 🧪 테스트 데이터 생성

### 8.1 샘플 데이터 생성
```python
# management/commands/generate_sample_data.py 생성 필요
class Command(BaseCommand):
    def handle(self, *args, **options):
        """실제 테스트용 샘플 데이터 생성"""
        # TODO: 실제 치과 데이터 생성
        # TODO: 샘플 리뷰 데이터 생성
        # TODO: 감성 분석 결과 생성
        pass
```

### 8.2 성능 테스트 데이터
```python
# scripts/load_test_data.py 생성 필요
def create_large_dataset():
    """대용량 테스트 데이터 생성"""
    # TODO: 10,000개 이상의 리뷰 데이터 생성
    # TODO: 성능 테스트용 데이터 생성
    pass
```

## 9. 📈 모니터링 및 로깅

### 9.1 상세 로깅 시스템
```python
# utils/logging.py 생성 필요
class DetailedLogger:
    def log_crawling_activity(self, clinic_id, source, status):
        """크롤링 활동 상세 로깅"""
        pass
    
    def log_recommendation_request(self, user_id, district, results):
        """추천 요청 로깅"""
        pass
```

### 9.2 성능 메트릭 수집
```python
# utils/metrics.py 생성 필요
class MetricsCollector:
    def track_api_response_time(self, endpoint, duration):
        """API 응답 시간 추적"""
        pass
    
    def track_ml_model_performance(self, model_name, accuracy):
        """ML 모델 성능 추적"""
        pass
```

## 10. 🔒 보안 강화

### 10.1 API 보안
- **Rate Limiting**: 더 세밀한 요청 제한
- **API Key 관리**: 외부 API 키 안전한 관리
- **입력 검증**: 더 강화된 입력 데이터 검증

### 10.2 데이터 보안
- **개인정보 암호화**: 민감한 데이터 암호화 저장
- **접근 로그**: 데이터 접근 기록 관리
- **백업 암호화**: 데이터베이스 백업 암호화

## 📝 구현 우선순위

### 🔥 높은 우선순위 (즉시 구현 필요)
1. **크롤링 로직 완성** - 실제 데이터 수집을 위해 필수
2. **기본 감성 분석** - 규칙 기반이라도 기본 기능 구현
3. **추천 알고리즘** - 핵심 비즈니스 로직
4. **샘플 데이터 생성** - 테스트 및 데모용

### 🔶 중간 우선순위 (단계적 구현)
1. **ML 모델 훈련** - 정확도 향상을 위해
2. **성능 최적화** - 사용자 증가에 대비
3. **모니터링 시스템** - 운영 안정성 확보
4. **프론트엔드** - 사용자 경험 개선

### 🔷 낮은 우선순위 (장기적 개선)
1. **고급 보안 기능** - 서비스 성숙도에 따라
2. **상세 분석 기능** - 비즈니스 요구에 따라
3. **외부 API 연동** - 추가 데이터 소스 확보

## 🛠️ 개발 환경 설정

### IDE 설정
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black"
}
```

### 개발 도구
```bash
# 코드 품질 도구 설치
pip install black isort flake8 mypy

# 개발용 의존성
pip install django-debug-toolbar django-extensions
```

이 가이드를 참고하여 단계적으로 시스템을 완성해 나가시면 됩니다!