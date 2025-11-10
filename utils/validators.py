"""
Custom validators for the dental AI system
"""
import re
from typing import Optional, Tuple
from django.core.exceptions import ValidationError


def validate_korean_district(value: str) -> None:
    """
    한국 지역구 이름 유효성 검사
    """
    if not value:
        raise ValidationError('지역구를 입력해주세요.')
    
    # 한글과 기본 문자만 허용
    if not re.match(r'^[가-힣\s]+$', value):
        raise ValidationError('지역구는 한글로만 입력해주세요.')
    
    # 길이 제한
    if len(value) < 2 or len(value) > 20:
        raise ValidationError('지역구는 2-20자 사이로 입력해주세요.')


def validate_phone_number(value: str) -> None:
    """
    전화번호 유효성 검사
    """
    if not value:
        return  # 선택적 필드인 경우
    
    # 한국 전화번호 패턴
    phone_pattern = r'^(010|011|016|017|018|019|02|031|032|033|041|042|043|044|051|052|053|054|055|061|062|063|064)-?\d{3,4}-?\d{4}$'
    
    if not re.match(phone_pattern, value.replace(' ', '').replace('-', '')):
        raise ValidationError('올바른 전화번호 형식이 아닙니다.')


def validate_price_range(price: int, treatment_type: str) -> bool:
    """
    치료별 가격 범위 유효성 검사
    """
    # 치료별 일반적인 가격 범위 (원)
    price_ranges = {
        'scaling': (30000, 200000),      # 스케일링
        'implant': (800000, 3000000),    # 임플란트
        'root_canal': (100000, 500000),  # 신경치료
        'orthodontics': (2000000, 8000000),  # 교정
        'whitening': (200000, 800000),   # 미백
        'extraction': (50000, 300000),   # 발치
        'filling': (50000, 300000),      # 충치치료
        'crown': (300000, 1000000),      # 크라운
        'bridge': (500000, 2000000),     # 브릿지
        'denture': (1000000, 5000000),   # 틀니
    }
    
    if treatment_type not in price_ranges:
        return True  # 알 수 없는 치료는 통과
    
    min_price, max_price = price_ranges[treatment_type]
    return min_price <= price <= max_price


def validate_sentiment_score(score: float) -> None:
    """
    감성 점수 유효성 검사 (-1 ~ +1)
    """
    if not isinstance(score, (int, float)):
        raise ValidationError('감성 점수는 숫자여야 합니다.')
    
    if not -1.0 <= score <= 1.0:
        raise ValidationError('감성 점수는 -1.0과 1.0 사이의 값이어야 합니다.')


def validate_coordinates(latitude: float, longitude: float) -> None:
    """
    위도, 경도 유효성 검사 (한국 범위)
    """
    # 한국의 대략적인 좌표 범위
    korea_lat_range = (33.0, 39.0)  # 위도
    korea_lng_range = (124.0, 132.0)  # 경도
    
    if not (korea_lat_range[0] <= latitude <= korea_lat_range[1]):
        raise ValidationError('위도가 한국 범위를 벗어났습니다.')
    
    if not (korea_lng_range[0] <= longitude <= korea_lng_range[1]):
        raise ValidationError('경도가 한국 범위를 벗어났습니다.')


def extract_price_from_text(text: str) -> Optional[Tuple[int, str]]:
    """
    텍스트에서 가격 정보 추출
    Returns: (price, currency) or None
    """
    if not text:
        return None
    
    # 한국어 가격 패턴들
    patterns = [
        r'(\d{1,3}(?:,\d{3})*)\s*원',  # 10,000원
        r'(\d+)\s*만\s*원',           # 10만원
        r'(\d+)\s*천\s*원',           # 5천원
        r'(\d{1,3}(?:,\d{3})*)\s*₩',  # 10,000₩
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            price_str = matches[0].replace(',', '')
            try:
                if '만' in pattern:
                    price = int(price_str) * 10000
                elif '천' in pattern:
                    price = int(price_str) * 1000
                else:
                    price = int(price_str)
                
                # 합리적인 가격 범위 확인 (1,000원 ~ 10,000,000원)
                if 1000 <= price <= 10000000:
                    return (price, 'KRW')
            except ValueError:
                continue
    
    return None


def classify_treatment_from_text(text: str) -> Optional[str]:
    """
    텍스트에서 치료 종류 분류
    """
    if not text:
        return None
    
    # 치료별 키워드 매핑
    treatment_keywords = {
        'scaling': ['스케일링', '치석제거', '치석 제거', '잇몸치료'],
        'implant': ['임플란트', '인플란트', '임플', '인공치아'],
        'root_canal': ['신경치료', '근관치료', '신경', '뿌리치료'],
        'orthodontics': ['교정', '치아교정', '브라켓', '투명교정', '인비절라인'],
        'whitening': ['미백', '치아미백', '화이트닝', '미백치료'],
        'extraction': ['발치', '뽑기', '사랑니', '치아제거'],
        'filling': ['충치', '충치치료', '때우기', '레진', '아말감'],
        'crown': ['크라운', '씌우기', '금니', '세라믹'],
        'bridge': ['브릿지', '브리지', '연결'],
        'denture': ['틀니', '의치', '부분틀니', '전체틀니'],
    }
    
    text_lower = text.lower()
    
    for treatment, keywords in treatment_keywords.items():
        for keyword in keywords:
            if keyword in text_lower:
                return treatment
    
    return 'other'  # 분류되지 않은 경우