# 치과 추천 AI - 프론트엔드

React + Vite 기반의 치과 추천 AI 시스템 프론트엔드입니다.

## 🚀 시작하기

### 설치

```bash
# 의존성 설치
npm install

# 환경 변수 설정
cp .env.example .env
```

### 개발 서버 실행

```bash
npm run dev
```

개발 서버가 http://localhost:3000에서 실행됩니다.

### 빌드

```bash
# 프로덕션 빌드
npm run build

# 빌드 결과 미리보기
npm run preview
```

## 📁 프로젝트 구조

```
src/
├── components/          # 재사용 가능한 컴포넌트
│   ├── common/         # 공통 컴포넌트
│   ├── layout/         # 레이아웃 컴포넌트
│   ├── clinic/         # 치과 관련 컴포넌트
│   └── search/         # 검색 관련 컴포넌트
├── pages/              # 페이지 컴포넌트
├── contexts/           # React Context
├── services/           # API 서비스
├── styles/             # 스타일 관련
│   ├── GlobalStyle.js  # 전역 스타일
│   └── theme.js        # 테마 설정
└── App.jsx             # 메인 앱 컴포넌트
```

## 🎨 디자인 시스템

### 컬러 팔레트
- **Primary**: #2c5aa0 (메인 블루)
- **Secondary**: #00c851 (포인트 그린)
- **Accent**: #ff6b35 (강조 오렌지)

### 타이포그래피
- **Font Family**: Noto Sans KR
- **Font Sizes**: 12px ~ 48px (responsive)

### 컴포넌트
- 모든 아이콘은 CSS로 구현 (유니코드 아이콘 사용 안함)
- 반응형 디자인 적용
- 참고 사이트 스타일 기반

## 🔧 주요 기능

### 페이지
- **홈페이지**: 메인 검색 및 서비스 소개
- **검색페이지**: 치과 검색 및 필터링
- **치과 상세**: 치과 정보 및 리뷰 분석
- **로그인/회원가입**: 사용자 인증
- **마이페이지**: 사용자 정보 관리

### 컴포넌트
- **Header**: 네비게이션 및 사용자 메뉴
- **Footer**: 사이트 정보 및 링크
- **ClinicCard**: 치과 정보 카드
- **SearchFilters**: 검색 필터
- **LoadingSpinner**: 로딩 인디케이터

## 🌐 API 연동

### 인증
- JWT 토큰 기반 인증
- 자동 토큰 갱신
- 로그인 상태 관리

### 엔드포인트
- `/api/auth/*` - 인증 관련
- `/api/clinics/*` - 치과 정보
- `/api/reviews/*` - 리뷰 데이터
- `/api/recommend/` - AI 추천

## 📱 반응형 디자인

### 브레이크포인트
- **Mobile**: 480px 이하
- **Tablet**: 768px 이하
- **Desktop**: 1024px 이하
- **Wide**: 1200px 이상

### 반응형 특징
- 모바일 우선 설계
- 터치 친화적 인터페이스
- 적응형 레이아웃

## 🔒 보안

### 클라이언트 보안
- XSS 방지
- CSRF 토큰 처리
- 안전한 토큰 저장
- 입력 데이터 검증

## 🚀 배포

### 빌드 최적화
- 코드 스플리팅
- 이미지 최적화
- CSS 압축
- 번들 크기 최적화

### 환경 변수
```bash
VITE_API_URL=https://api.dental-ai.com/api
```

## 🛠️ 개발 도구

### 코드 품질
- ESLint 설정
- Prettier 포맷팅
- 컴포넌트 prop-types

### 디버깅
- React Developer Tools
- 네트워크 요청 로깅
- 에러 바운더리

## 📚 사용된 라이브러리

- **React 18**: UI 라이브러리
- **React Router**: 라우팅
- **Styled Components**: CSS-in-JS
- **Axios**: HTTP 클라이언트
- **Vite**: 빌드 도구

## 🤝 기여하기

1. 코드 스타일 가이드 준수
2. 컴포넌트 재사용성 고려
3. 접근성 가이드라인 준수
4. 성능 최적화 고려