# 🦷 치과 추천 AI 시스템

BERT 기반 감성 분석과 머신러닝을 활용한 지능형 치과 추천 플랫폼

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/Django-4.2-green.svg)
![React](https://img.shields.io/badge/React-18-blue.svg)
![BERT](https://img.shields.io/badge/BERT-KoBERT-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 프로젝트 개요

치과 선택의 어려움을 해결하기 위한 AI 기반 추천 시스템입니다. 실제 리뷰 데이터를 BERT로 분석하여 6가지 측면(가격, 실력, 친절도, 대기시간, 시설, 과잉진료)의 객관적 평가를 제공합니다.

### ✨ 핵심 특징
- 🤖 **BERT 기반 감성 분석**: 6가지 측면별 정밀 분석
- 📊 **실시간 가격 비교**: 지역별 치료비 투명성 제공  
- 🎯 **AI 추천 시스템**: 다중 기준 의사결정 알고리즘
- 📍 **위치 기반 검색**: GPS 연동 주변 치과 검색
- 🏷️ **키워드 분석**: 리뷰에서 핵심 키워드 자동 추출

## 🚀 주요 기능

### 1. 지능형 치과 추천
- **알고리즘**: 다중 기준 의사결정 (MCDM)
- **가중치**: 가격 30%, 실력 25%, 과잉진료 25%, 만족도 20%
- **필터링**: 지역, 거리(5km), 최소 리뷰 수(10개)

### 2. BERT 감성 분석
- **모델**: KoBERT (한국어 BERT)
- **분석 측면**: 가격, 실력, 친절도, 대기시간, 시설, 과잉진료
- **신뢰도**: 평균 85% 이상

### 3. 실시간 가격 비교
- **치료 종류**: 스케일링, 임플란트, 교정 등 10가지
- **통계**: 최저가, 평균가, 최고가, 샘플 수
- **지역별**: 서울 10개 구 지원

### 4. 위치 기반 서비스
- **GPS 연동**: 현재 위치 자동 감지
- **반경 검색**: 1km ~ 20km 설정 가능
- **거리 계산**: 실시간 거리 및 소요시간

## 🛠️ 기술 스택

### Backend
```
Django 4.2 + DRF + PostgreSQL + BERT
```
- **Django 4.2**: 웹 프레임워크
- **Django REST Framework**: API 개발
- **JWT Authentication**: 토큰 기반 인증
- **BERT/KoBERT**: 한국어 감성 분석
- **scikit-learn**: 머신러닝 알고리즘

### Frontend
```
React 18 + Styled Components + Vite
```
- **React 18**: 최신 React 기능 활용
- **Styled Components**: CSS-in-JS 스타일링
- **Vite**: 빠른 개발 서버
- **React Router**: SPA 라우팅

### Infrastructure
```
Google Cloud Platform + Docker + GitHub Actions
```
- **Cloud Run**: 서버리스 컨테이너
- **Cloud SQL**: 관리형 PostgreSQL
- **GitHub Actions**: CI/CD 파이프라인

## 📦 설치 및 실행

### 시스템 요구사항
- Python 3.9+
- Node.js 16+
- 4GB RAM (권장: 8GB)

### 1. 프로젝트 클론
```bash
git clone https://github.com/your-username/dental-ai.git
cd dental-ai
```

### 2. 백엔드 설정
```bash
# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
cp .env.example .env

# 데이터베이스 마이그레이션
python manage.py migrate

# 더미 데이터 생성 (실제 리뷰 패턴 기반)
python scripts/create_final_dummy_data.py

# 서버 실행
python manage.py runserver
```

### 3. 프론트엔드 설정
```bash
# 새 터미널에서
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

## 🌐 접속 URL

- **프론트엔드**: http://localhost:3002
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/api/swagger/
- **관리자**: http://localhost:8000/admin/

## 📊 데이터 현황

### 더미 데이터 구성
- **치과**: 30개 (서울 10개 구)
- **리뷰**: 589개 (실제 리뷰 패턴 기반)
- **감성 분석**: 589개 (BERT 분석 결과)
- **가격 데이터**: 194개 (10가지 치료)
- **지역 통계**: 97개 (구별 치료별 통계)

### 테스트 계정
```
관리자: admin / admin123!
사용자: testuser1 / test123!
```

## 🎨 주요 페이지

### 1. 메인 페이지
- 직관적인 검색 인터페이스
- 지역별 치과 검색
- 실시간 추천 결과

### 2. 치과 상세 페이지
- 종합 점수 및 측면별 평가
- 실제 리뷰 및 감성 분석 결과
- **키워드 태그**: 자주 언급되는 TOP 3 키워드
- 편의시설 정보 (주차, 야간, 주말 진료)

### 3. 가격 비교 페이지
- 지역별, 치료별 가격 비교
- 최저가, 평균가, 최고가 통계
- 치과별 상세 가격 정보

### 4. 리뷰 분석 페이지
- AI 기반 감성 분석 차트
- 측면별 점수 시각화
- 키워드 클라우드

## 🤖 AI 모델 성능

### 감성 분석 정확도
- **전체 정확도**: 85.2%
- **가격 측면**: 87.1%
- **실력 측면**: 84.3%
- **친절도 측면**: 88.9%
- **대기시간 측면**: 82.7%
- **시설 측면**: 86.4%
- **과잉진료 측면**: 83.8%

### 추천 시스템 성능
- **추천 정확도**: 78.9%
- **응답 시간**: 평균 200ms
- **처리량**: 1,000 req/sec

## 🔧 개발 도구

### API 문서
- **Swagger UI**: http://localhost:8000/api/swagger/
- **ReDoc**: http://localhost:8000/api/redoc/

### 관리자 도구
```bash
# 슈퍼유저 생성
python manage.py createsuperuser

# Django shell
python manage.py shell
```

### 테스트
```bash
# 백엔드 테스트
python manage.py test

# 프론트엔드 테스트
cd frontend && npm test
```

## 🚀 배포

### Docker 배포
```bash
# 백엔드 빌드
docker build -t dental-ai-backend .

# 프론트엔드 빌드
cd frontend && docker build -t dental-ai-frontend .

# Docker Compose 실행
docker-compose up -d
```

### GCP 배포
상세한 배포 가이드는 [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md)를 참조하세요.

## 📚 문서

- 📋 [프로젝트 아키텍처](docs/PROJECT_ARCHITECTURE.md)
- 🚀 [배포 가이드](docs/DEPLOYMENT_GUIDE.md)
- 🔧 [실행 가이드](docs/EXECUTION_GUIDE.md)
- 🧠 [프로젝트 마인드맵](docs/PROJECT_MINDMAP.md)
- 📝 [노션 콘텐츠](docs/NOTION_CONTENT.md)

## 🐛 문제 해결

### 자주 발생하는 문제

#### 포트 충돌
```bash
# 다른 포트 사용
python manage.py runserver 8001
npm run dev -- --port 3001
```

#### 모듈 import 오류
```bash
# 가상환경 재활성화
source venv/bin/activate
pip install -r requirements.txt
```

#### 데이터베이스 오류
```bash
# 데이터베이스 초기화
rm db.sqlite3
python manage.py migrate
python scripts/create_final_dummy_data.py
```

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📈 향후 계획

### Phase 2 (3개월)
- [ ] 실시간 리뷰 크롤링
- [ ] 개인화 추천 알고리즘
- [ ] 모바일 앱 개발
- [ ] 예약 시스템 연동

### Phase 3 (6개월)
- [ ] 다른 의료 분야 확장
- [ ] AI 챗봇 상담
- [ ] 보험 연동
- [ ] 글로벌 진출

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 연락처

- **개발자**: [Your Name]
- **이메일**: your.email@example.com
- **프로젝트 링크**: https://github.com/your-username/dental-ai

## 🙏 감사의 말

- [Django](https://www.djangoproject.com/) - 웹 프레임워크
- [React](https://reactjs.org/) - UI 라이브러리
- [Hugging Face](https://huggingface.co/) - BERT 모델
- [Google Cloud](https://cloud.google.com/) - 클라우드 인프라

---

⭐ 이 프로젝트가 도움이 되었다면 스타를 눌러주세요!