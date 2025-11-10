# 설계 문서

## 개요

치과 추천 AI 시스템은 Django 5.0과 Django REST Framework를 기반으로 하는 마이크로서비스 아키텍처를 채택합니다. 시스템은 리뷰 크롤링, 감성 분석, 가격 추출, 추천 알고리즘의 4개 핵심 모듈로 구성되며, PostgreSQL과 Redis를 활용한 데이터 저장 및 캐싱 전략을 사용합니다.

## 아키텍처

### 전체 시스템 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Django API    │    │   ML Services   │
│   (Web/Mobile)  │◄──►│   Gateway       │◄──►│   (Sentiment)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   PostgreSQL    │
                       │   Database      │
                       └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │     Redis       │◄──►│     Celery      │
                       │    Cache        │    │   Task Queue    │
                       └─────────────────┘    └─────────────────┘
```

### Django 앱 구조

```
dental_project/
├── config/                 # Django 설정
├── apps/
│   ├── accounts/          # 사용자 인증 및 관리
│   ├── clinics/           # 치과 정보 관리
│   ├── reviews/           # 리뷰 데이터 관리
│   ├── analysis/          # ML 감성 분석
│   ├── recommendations/   # 추천 알고리즘
│   └── api/              # REST API 엔드포인트
├── ml_models/            # 머신러닝 모델 저장소
├── tasks/                # Celery 태스크
└── utils/                # 공통 유틸리티
```

## 컴포넌트 및 인터페이스

### 1. 리뷰 크롤링 모듈 (apps/reviews/)

**주요 컴포넌트:**
- `NaverCrawler`: 네이버 플레이스 리뷰 수집
- `GoogleCrawler`: 구글 맵 리뷰 수집  
- `ReviewProcessor`: 리뷰 전처리 및 정제
- `AnonymizationService`: 개인정보 익명화

**인터페이스:**
```python
class BaseCrawler:
    def crawl_reviews(self, clinic_id: str, max_reviews: int = 100) -> List[RawReview]
    def validate_review(self, review: RawReview) -> bool
    
class ReviewProcessor:
    def preprocess_text(self, text: str) -> str
    def remove_duplicates(self, reviews: List[RawReview]) -> List[RawReview]
    def anonymize_personal_info(self, text: str) -> str
```

### 2. 감성 분석 모듈 (apps/analysis/)

**주요 컴포넌트:**
- `ABSAEngine`: Aspect-Based Sentiment Analysis 엔진
- `KoBERTAnalyzer`: KoBERT 기반 감성 분석
- `SVMAnalyzer`: SVM + TF-IDF 대체 분석기
- `AspectExtractor`: 6가지 측면 추출기

**인터페이스:**
```python
class ABSAEngine:
    def analyze_review(self, review_text: str) -> AspectScores
    def extract_aspects(self, text: str) -> Dict[str, List[str]]
    def calculate_sentiment_score(self, text: str, aspect: str) -> float
    
class AspectScores:
    price: float          # -1 ~ +1
    skill: float          # -1 ~ +1  
    kindness: float       # -1 ~ +1
    waiting_time: float   # -1 ~ +1
    facility: float       # -1 ~ +1
    overtreatment: float  # -1 ~ +1
```

### 3. 가격 추출 모듈 (apps/analysis/)

**주요 컴포넌트:**
- `PriceExtractor`: NER 기반 가격 정보 추출
- `TreatmentClassifier`: 치료 종류 분류기
- `PriceValidator`: 가격 데이터 검증
- `RegionalPriceCalculator`: 지역별 평균가 계산

**인터페이스:**
```python
class PriceExtractor:
    def extract_prices(self, review_text: str) -> List[PriceInfo]
    def classify_treatment(self, context: str) -> TreatmentType
    def validate_price_range(self, price: int, treatment: str) -> bool
    
class PriceInfo:
    treatment_type: str
    price: int
    currency: str = "KRW"
    confidence: float
```

### 4. 추천 알고리즘 모듈 (apps/recommendations/)

**주요 컴포넌트:**
- `RecommendationEngine`: 종합 추천 엔진
- `ScoreCalculator`: 점수 계산기
- `LocationFilter`: 지역 기반 필터링
- `ExplanationGenerator`: 추천 이유 생성기

**인터페이스:**
```python
class RecommendationEngine:
    def get_recommendations(self, district: str, filters: Dict) -> List[Recommendation]
    def calculate_comprehensive_score(self, clinic: Clinic) -> float
    def generate_explanation(self, clinic: Clinic, score: float) -> str
    
class Recommendation:
    clinic: Clinic
    score: float
    explanation: str
    price_competitiveness: float
    overtreatment_risk: float
```

## 데이터 모델

### 핵심 모델 구조

```python
# apps/clinics/models.py
class Clinic(models.Model):
    name = models.CharField(max_length=200)
    address = models.TextField()
    district = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    phone = models.CharField(max_length=20)
    
    # 시설 정보
    has_parking = models.BooleanField(default=False)
    night_service = models.BooleanField(default=False)
    weekend_service = models.BooleanField(default=False)
    
    # 통계 정보
    total_reviews = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# apps/reviews/models.py  
class Review(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='reviews')
    source = models.CharField(max_length=20, choices=[('naver', '네이버'), ('google', '구글')])
    original_text = models.TextField()
    processed_text = models.TextField()
    
    # 원본 메타데이터
    original_rating = models.IntegerField(null=True)
    review_date = models.DateTimeField(null=True)
    reviewer_hash = models.CharField(max_length=64)  # 익명화된 리뷰어 식별자
    
    # 처리 상태
    is_processed = models.BooleanField(default=False)
    is_duplicate = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

# apps/analysis/models.py
class SentimentAnalysis(models.Model):
    review = models.OneToOneField(Review, on_delete=models.CASCADE)
    
    # 6가지 측면별 점수 (-1 ~ +1)
    price_score = models.DecimalField(max_digits=3, decimal_places=2)
    skill_score = models.DecimalField(max_digits=3, decimal_places=2)
    kindness_score = models.DecimalField(max_digits=3, decimal_places=2)
    waiting_time_score = models.DecimalField(max_digits=3, decimal_places=2)
    facility_score = models.DecimalField(max_digits=3, decimal_places=2)
    overtreatment_score = models.DecimalField(max_digits=3, decimal_places=2)
    
    # 분석 메타데이터
    model_version = models.CharField(max_length=50)
    confidence_score = models.DecimalField(max_digits=3, decimal_places=2)
    analyzed_at = models.DateTimeField(auto_now_add=True)

class PriceData(models.Model):
    clinic = models.ForeignKey(Clinic, on_delete=models.CASCADE, related_name='prices')
    review = models.ForeignKey(Review, on_delete=models.CASCADE, null=True)
    
    treatment_type = models.CharField(max_length=100)
    price = models.IntegerField()
    currency = models.CharField(max_length=3, default='KRW')
    
    # 추출 메타데이터
    extraction_confidence = models.DecimalField(max_digits=3, decimal_places=2)
    extraction_method = models.CharField(max_length=50)  # 'regex', 'ner', 'manual'
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['treatment_type', 'clinic__district']),
        ]

# apps/recommendations/models.py
class RecommendationLog(models.Model):
    user = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    district = models.CharField(max_length=100)
    treatment_type = models.CharField(max_length=100, null=True)
    
    # 추천 결과
    recommended_clinics = models.JSONField()  # 추천된 치과 ID 목록
    algorithm_version = models.CharField(max_length=50)
    
    created_at = models.DateTimeField(auto_now_add=True)
```

### PostgreSQL 전문 검색 설정

```python
# apps/reviews/models.py에 추가
class Review(models.Model):
    # ... 기존 필드들 ...
    
    # PostgreSQL 전문 검색을 위한 벡터 필드
    search_vector = SearchVectorField(null=True)
    
    class Meta:
        indexes = [
            GinIndex(fields=['search_vector']),
            models.Index(fields=['clinic', 'is_processed']),
        ]
```

## 오류 처리

### 1. 크롤링 오류 처리

```python
class CrawlingError(Exception):
    pass

class RateLimitError(CrawlingError):
    pass

class InvalidResponseError(CrawlingError):
    pass

# 재시도 로직
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def crawl_with_retry(crawler, clinic_id):
    try:
        return crawler.crawl_reviews(clinic_id)
    except RateLimitError:
        time.sleep(60)  # 1분 대기 후 재시도
        raise
```

### 2. ML 모델 오류 처리

```python
class MLModelError(Exception):
    pass

class ModelNotFoundError(MLModelError):
    pass

class PredictionError(MLModelError):
    pass

# 대체 모델 사용
def analyze_with_fallback(text: str) -> AspectScores:
    try:
        return kobert_analyzer.analyze(text)
    except ModelNotFoundError:
        logger.warning("KoBERT 모델을 찾을 수 없음. SVM 모델로 대체")
        return svm_analyzer.analyze(text)
    except PredictionError as e:
        logger.error(f"감성 분석 실패: {e}")
        return AspectScores.default()  # 기본값 반환
```

### 3. API 오류 처리

```python
# apps/api/exceptions.py
class APIException(Exception):
    status_code = 500
    default_message = "서버 오류가 발생했습니다"

class ValidationError(APIException):
    status_code = 400
    default_message = "입력 데이터가 올바르지 않습니다"

class NotFoundError(APIException):
    status_code = 404
    default_message = "요청한 리소스를 찾을 수 없습니다"

# 전역 예외 처리기
def custom_exception_handler(exc, context):
    if isinstance(exc, APIException):
        return Response({
            'error': exc.default_message,
            'code': exc.__class__.__name__
        }, status=exc.status_code)
    
    return default_exception_handler(exc, context)
```

## 테스트 전략

### 1. 단위 테스트

```python
# tests/test_analysis.py
class TestABSAEngine(TestCase):
    def setUp(self):
        self.engine = ABSAEngine()
    
    def test_price_sentiment_analysis(self):
        text = "가격이 너무 비싸서 부담스러웠어요"
        scores = self.engine.analyze_review(text)
        self.assertLess(scores.price, 0)  # 부정적 점수 확인
    
    def test_skill_sentiment_analysis(self):
        text = "의사선생님이 정말 꼼꼼하고 실력이 좋으세요"
        scores = self.engine.analyze_review(text)
        self.assertGreater(scores.skill, 0)  # 긍정적 점수 확인

# tests/test_price_extraction.py  
class TestPriceExtractor(TestCase):
    def test_extract_scaling_price(self):
        text = "스케일링 받았는데 3만원이었어요"
        extractor = PriceExtractor()
        prices = extractor.extract_prices(text)
        
        self.assertEqual(len(prices), 1)
        self.assertEqual(prices[0].treatment_type, "스케일링")
        self.assertEqual(prices[0].price, 30000)
```

### 2. 통합 테스트

```python
# tests/test_recommendation_flow.py
class TestRecommendationFlow(TestCase):
    def test_full_recommendation_pipeline(self):
        # 1. 테스트 데이터 생성
        clinic = Clinic.objects.create(name="테스트치과", district="강남구")
        
        # 2. 리뷰 생성 및 분석
        review = Review.objects.create(
            clinic=clinic,
            original_text="가격도 합리적이고 의사선생님이 친절해요"
        )
        
        # 3. 감성 분석 실행
        analysis_task = analyze_review.delay(review.id)
        analysis_task.get()
        
        # 4. 추천 요청
        response = self.client.post('/api/recommend/', {
            'district': '강남구'
        })
        
        # 5. 결과 검증
        self.assertEqual(response.status_code, 200)
        self.assertIn('recommendations', response.json())
```

### 3. 성능 테스트

```python
# tests/test_performance.py
class TestPerformance(TestCase):
    def test_recommendation_response_time(self):
        start_time = time.time()
        
        response = self.client.post('/api/recommend/', {
            'district': '강남구'
        })
        
        end_time = time.time()
        response_time = end_time - start_time
        
        self.assertLess(response_time, 3.0)  # 3초 이내 응답
        self.assertEqual(response.status_code, 200)
    
    def test_concurrent_requests(self):
        # 동시 요청 100개 처리 테스트
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = []
            for _ in range(100):
                future = executor.submit(self.make_recommendation_request)
                futures.append(future)
            
            # 모든 요청이 성공적으로 처리되는지 확인
            for future in futures:
                response = future.result()
                self.assertEqual(response.status_code, 200)
```

이 설계는 확장 가능하고 유지보수가 용이한 구조로 되어 있으며, 각 컴포넌트가 독립적으로 테스트 가능하도록 설계되었습니다.