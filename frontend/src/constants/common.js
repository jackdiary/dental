// 공통 상수 정의

// 서울시 전체 자치구 목록 (25개)
export const SEOUL_DISTRICTS = [
  '강남구',
  '강동구', 
  '강북구',
  '강서구',
  '관악구',
  '광진구',
  '구로구',
  '금천구',
  '노원구',
  '도봉구',
  '동대문구',
  '동작구',
  '마포구',
  '서대문구',
  '서초구',
  '성동구',
  '성북구',
  '송파구',
  '양천구',
  '영등포구',
  '용산구',
  '은평구',
  '종로구',
  '중구',
  '중랑구'
];

// 치료 종류 목록 (한국어)
export const TREATMENT_TYPES = [
  '스케일링',
  '임플란트',
  '교정',
  '미백',
  '신경치료',
  '발치',
  '충치치료',
  '크라운',
  '브릿지',
  '틀니',
  '사랑니',
  '잇몸치료'
];

// 치료 종류 매핑 (영어 ↔ 한국어)
export const TREATMENT_MAPPING = {
  // 영어 → 한국어
  'scaling': '스케일링',
  'implant': '임플란트',
  'orthodontics': '교정',
  'whitening': '미백',
  'root_canal': '신경치료',
  'extraction': '발치',
  'filling': '충치치료',
  'crown': '크라운',
  'bridge': '브릿지',
  'denture': '틀니',
  'wisdom_tooth': '사랑니',
  'gum_treatment': '잇몸치료',
  
  // 한국어 → 영어 (역방향)
  '스케일링': 'scaling',
  '임플란트': 'implant',
  '교정': 'orthodontics',
  '미백': 'whitening',
  '신경치료': 'root_canal',
  '발치': 'extraction',
  '충치치료': 'filling',
  '크라운': 'crown',
  '브릿지': 'bridge',
  '틀니': 'denture',
  '사랑니': 'wisdom_tooth',
  '잇몸치료': 'gum_treatment'
};

// 치료 종류 변환 함수
export const getTreatmentName = (treatment) => {
  // 이미 한국어인 경우 그대로 반환
  if (TREATMENT_TYPES.includes(treatment)) {
    return treatment;
  }
  
  // 영어인 경우 한국어로 변환
  return TREATMENT_MAPPING[treatment] || treatment;
};

// 치료 종류를 영어로 변환
export const getTreatmentCode = (treatment) => {
  // 이미 영어인 경우 그대로 반환
  if (Object.keys(TREATMENT_MAPPING).includes(treatment) && !TREATMENT_TYPES.includes(treatment)) {
    return treatment;
  }
  
  // 한국어인 경우 영어로 변환
  return TREATMENT_MAPPING[treatment] || treatment;
};

// 측면별 라벨 매핑
export const ASPECT_LABELS = {
  price: '가격',
  skill: '실력', 
  kindness: '친절도',
  waiting_time: '대기시간',
  facility: '시설',
  overtreatment: '과잉진료'
};

// 편의시설 옵션
export const FACILITY_OPTIONS = [
  { key: 'parking', label: '주차 가능' },
  { key: 'night', label: '야간 진료' },
  { key: 'weekend', label: '주말 진료' },
  { key: 'no_overtreatment', label: '과잉진료 없음' }
];

// 정렬 옵션
export const SORT_OPTIONS = [
  { value: 'recommended', label: '추천순' },
  { value: 'rating', label: '평점순' },
  { value: 'reviews', label: '리뷰많은순' },
  { value: 'price', label: '가격순' },
  { value: 'distance', label: '거리순' }
];

// 평점 옵션
export const RATING_OPTIONS = [
  { value: '4.5', label: '4.5점 이상' },
  { value: '4.0', label: '4.0점 이상' },
  { value: '3.5', label: '3.5점 이상' },
  { value: '3.0', label: '3.0점 이상' }
];