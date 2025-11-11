# CORS 설정 수정 디자인 문서

## 개요

현재 Google Cloud Run에 배포된 Django 백엔드와 React 프론트엔드 간의 CORS 정책 오류를 해결하기 위한 설계입니다. 주요 문제는 `django-cors-headers` 설정의 충돌과 잘못된 와일드카드 패턴 사용입니다.

## 아키텍처

### 현재 문제점 분석

1. **설정 충돌**: `CORS_ALLOW_ALL_ORIGINS = True`와 `CORS_ALLOWED_ORIGINS` 리스트가 동시에 설정되어 있음
2. **잘못된 와일드카드**: `'https://*.run.app'` 패턴이 django-cors-headers에서 지원되지 않음
3. **미들웨어 순서**: CORS 미들웨어가 올바른 위치에 있지만 설정이 잘못됨
4. **환경별 설정 부족**: 개발/프로덕션 환경에 따른 적절한 CORS 정책 구분 없음

### 해결 방안 아키텍처

```
Frontend (Cloud Run) → CORS Headers → Backend (Cloud Run)
                    ↓
            Environment-specific
            CORS Configuration
                    ↓
            Logging & Debugging
```

## 컴포넌트 및 인터페이스

### 1. CORS 설정 관리자 (CORSConfigManager)

**역할**: 환경별 CORS 설정을 관리하고 검증

**인터페이스**:
```python
class CORSConfigManager:
    def get_allowed_origins(environment: str) -> List[str]
    def validate_cors_settings() -> bool
    def log_cors_configuration() -> None
```

### 2. 환경 감지기 (EnvironmentDetector)

**역할**: 현재 실행 환경을 감지하고 적절한 설정 적용

**인터페이스**:
```python
class EnvironmentDetector:
    def is_production() -> bool
    def is_development() -> bool
    def get_current_domain() -> str
```

### 3. CORS 디버깅 유틸리티 (CORSDebugger)

**역할**: CORS 관련 문제를 진단하고 로깅

**인터페이스**:
```python
class CORSDebugger:
    def log_cors_request(request, response) -> None
    def validate_cors_headers(response) -> Dict[str, Any]
    def create_health_check_response() -> HttpResponse
```

## 데이터 모델

### CORS 설정 구조

```python
CORS_SETTINGS = {
    'development': {
        'allowed_origins': [
            'http://localhost:3000',
            'http://127.0.0.1:3000',
            'http://localhost:5173',  # Vite 기본 포트
        ],
        'allow_all_origins': False,
        'allow_credentials': True,
    },
    'production': {
        'allowed_origins': [
            'https://dental-ai-frontend-602563947939.asia-northeast3.run.app',
            # 환경 변수에서 추가 도메인 로드
        ],
        'allow_all_origins': False,
        'allow_credentials': True,
    }
}
```

### 환경 변수 스키마

```bash
# 프로덕션 환경 변수
CORS_ALLOWED_ORIGINS=https://domain1.com,https://domain2.com
CORS_ALLOW_CREDENTIALS=true
CORS_DEBUG_MODE=false

# 개발 환경 변수
CORS_ALLOW_ALL_ORIGINS=true
CORS_DEBUG_MODE=true
```

## 오류 처리

### 1. CORS 오류 감지 및 로깅

```python
class CORSErrorHandler:
    def handle_cors_error(self, request, origin):
        logger.warning(f"CORS 요청 차단: {origin} -> {request.get_host()}")
        return JsonResponse({
            'error': 'CORS policy violation',
            'origin': origin,
            'allowed_origins': self.get_allowed_origins()
        }, status=403)
```

### 2. 설정 검증

```python
def validate_cors_configuration():
    """CORS 설정의 유효성을 검증"""
    errors = []
    
    if CORS_ALLOW_ALL_ORIGINS and CORS_ALLOWED_ORIGINS:
        errors.append("CORS_ALLOW_ALL_ORIGINS와 CORS_ALLOWED_ORIGINS를 동시에 설정할 수 없습니다")
    
    for origin in CORS_ALLOWED_ORIGINS:
        if '*' in origin and not origin.startswith('https://'):
            errors.append(f"잘못된 오리진 패턴: {origin}")
    
    return errors
```

## 테스트 전략

### 1. 단위 테스트

- CORS 설정 검증 함수 테스트
- 환경별 설정 로드 테스트
- 오리진 매칭 로직 테스트

### 2. 통합 테스트

- 실제 CORS 요청/응답 테스트
- 프리플라이트 요청 처리 테스트
- 다양한 오리진에서의 요청 테스트

### 3. 배포 테스트

- Cloud Run 환경에서의 CORS 동작 확인
- 프론트엔드-백엔드 통신 테스트
- 브라우저 개발자 도구를 통한 CORS 헤더 확인

## 구현 세부사항

### 1. 설정 파일 구조 개선

```python
# config/cors_settings.py
class CORSSettings:
    @staticmethod
    def get_production_settings():
        return {
            'CORS_ALLOWED_ORIGINS': [
                'https://dental-ai-frontend-602563947939.asia-northeast3.run.app',
            ],
            'CORS_ALLOW_CREDENTIALS': True,
            'CORS_ALLOW_ALL_ORIGINS': False,
        }
    
    @staticmethod
    def get_development_settings():
        return {
            'CORS_ALLOW_ALL_ORIGINS': True,
            'CORS_ALLOW_CREDENTIALS': True,
        }
```

### 2. 미들웨어 순서 최적화

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # 최상단에 위치
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    # ... 나머지 미들웨어
]
```

### 3. 헬스 체크 엔드포인트

```python
# apps/api/views.py
class CORSHealthCheckView(APIView):
    def get(self, request):
        return Response({
            'cors_enabled': True,
            'allowed_origins': settings.CORS_ALLOWED_ORIGINS,
            'allow_credentials': settings.CORS_ALLOW_CREDENTIALS,
            'current_origin': request.META.get('HTTP_ORIGIN'),
        })
```

## 보안 고려사항

1. **프로덕션 환경**: 특정 도메인만 허용
2. **개발 환경**: localhost 및 개발 서버만 허용
3. **로깅**: CORS 위반 시도를 모니터링
4. **환경 변수**: 민감한 설정은 환경 변수로 관리

## 성능 최적화

1. **캐싱**: CORS 설정을 메모리에 캐시
2. **조기 반환**: 허용되지 않은 오리진은 빠르게 차단
3. **로깅 최적화**: 프로덕션에서는 필요한 로그만 기록