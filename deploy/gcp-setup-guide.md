# Google Cloud Platform 설정 가이드

## 1. Google Cloud 프로젝트 생성

### 1.1 Google Cloud Console 접속
1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. Google 계정으로 로그인
3. 새 프로젝트 생성 또는 기존 프로젝트 선택

### 1.2 새 프로젝트 생성
```bash
# 프로젝트 ID 예시: dental-ai-2024
# 프로젝트 이름: 치과 추천 AI
```

1. 상단의 "프로젝트 선택" 드롭다운 클릭
2. "새 프로젝트" 클릭
3. 프로젝트 정보 입력:
   - **프로젝트 이름**: `치과 추천 AI`
   - **프로젝트 ID**: `dental-ai-2024` (고유해야 함)
   - **조직**: 개인 계정 사용
4. "만들기" 클릭

## 2. 필요한 API 활성화

### 2.1 Cloud Console에서 API 활성화
다음 API들을 활성화해야 합니다:

```bash
# 필수 API 목록
- Cloud Run API
- Cloud SQL Admin API
- Cloud Build API
- Container Registry API
- Cloud Storage API
- Cloud Logging API
- Cloud Monitoring API
- Compute Engine API
- Cloud Resource Manager API
- IAM Service Account Credentials API
```

### 2.2 API 활성화 방법
1. 좌측 메뉴에서 "API 및 서비스" > "라이브러리" 클릭
2. 각 API를 검색하여 "사용 설정" 클릭

또는 gcloud CLI로 일괄 활성화:
```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  storage.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com \
  compute.googleapis.com \
  cloudresourcemanager.googleapis.com \
  iamcredentials.googleapis.com
```

## 3. 결제 계정 설정

### 3.1 결제 계정 연결
1. 좌측 메뉴에서 "결제" 클릭
2. 기존 결제 계정 선택 또는 새 계정 생성
3. 신용카드 정보 입력

### 3.2 예산 알림 설정
1. "결제" > "예산 및 알림" 클릭
2. "예산 만들기" 클릭
3. 예산 설정:
   - **이름**: `치과AI 월별 예산`
   - **금액**: `$50` (초기 설정)
   - **알림 임계값**: `50%, 90%, 100%`

## 4. 무료 크레딧 확인

### 4.1 Google Cloud 무료 티어
- **$300 크레딧**: 90일간 사용 가능 (신규 사용자)
- **Always Free 티어**: 매월 무료 사용량 제공

### 4.2 주요 무료 티어 한도
```yaml
Cloud Run:
  - 요청: 2백만 건/월
  - CPU 시간: 180,000 vCPU-초/월
  - 메모리: 360,000 GiB-초/월

Cloud SQL:
  - db-f1-micro: 1개 인스턴스
  - 스토리지: 30GB/월

Cloud Storage:
  - 5GB 스토리지/월
  - 5,000 Class A 작업/월
  - 50,000 Class B 작업/월

Cloud Build:
  - 120 빌드 분/일
```

## 5. 프로젝트 설정 확인

### 5.1 프로젝트 ID 확인
```bash
gcloud config get-value project
```

### 5.2 활성화된 API 확인
```bash
gcloud services list --enabled
```

### 5.3 결제 계정 확인
```bash
gcloud beta billing accounts list
```

## 다음 단계

프로젝트 설정이 완료되면 다음 작업을 진행합니다:
1. **로컬 개발 환경 설정** (Google Cloud SDK 설치)
2. **프로젝트 구조 정리** (배포 설정 파일 생성)
3. **Django 프로덕션 설정** 생성

---

**⚠️ 중요 사항**
- 프로젝트 ID는 전 세계적으로 고유해야 합니다
- 무료 크레딧을 효율적으로 사용하기 위해 리소스 모니터링이 중요합니다
- 민감한 정보는 절대 코드에 하드코딩하지 마세요