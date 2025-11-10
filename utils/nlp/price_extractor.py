"""
가격 정보 추출 유틸리티
"""
import re
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class PriceInfo:
    treatment_type: str
    price: int
    confidence: float

class PriceExtractor:
    """리뷰에서 가격 정보 추출"""
    
    def __init__(self):
        # 치료 종류별 키워드
        self.treatment_keywords = {
            'scaling': ['스케일링', '치석제거', '잇몸치료'],
            'implant': ['임플란트', '인플란트', '임플'],
            'orthodontics': ['교정', '치아교정', '브라켓'],
            'whitening': ['미백', '화이트닝', '미백치료'],
            'root_canal': ['신경치료', '근관치료', '신경'],
            'extraction': ['발치', '사랑니', '뽑기'],
            'filling': ['충치', '때우기', '레진'],
            'crown': ['크라운', '씌우기', '보철']
        }
        
        # 가격 패턴 (만원, 원 단위)
        self.price_patterns = [
            r'(\d+)만원',
            r'(\d+)만\s*원',
            r'(\d{1,3}(?:,\d{3})*)원',
            r'(\d+)천원',
            r'(\d+)천\s*원'
        ]
    
    def extract_prices(self, text: str) -> List[PriceInfo]:
        """텍스트에서 가격 정보 추출"""
        results = []
        
        # 텍스트 정규화
        text = text.replace(',', '').replace(' ', '')
        
        for treatment_type, keywords in self.treatment_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    # 키워드 주변에서 가격 찾기
                    prices = self._find_prices_near_keyword(text, keyword)
                    for price, confidence in prices:
                        results.append(PriceInfo(
                            treatment_type=treatment_type,
                            price=price,
                            confidence=confidence
                        ))
        
        return results
    
    def _find_prices_near_keyword(self, text: str, keyword: str) -> List[tuple]:
        """키워드 주변에서 가격 찾기"""
        prices = []
        
        # 키워드 위치 찾기
        keyword_pos = text.find(keyword)
        if keyword_pos == -1:
            return prices
        
        # 키워드 앞뒤 50자 범위에서 가격 찾기
        start = max(0, keyword_pos - 50)
        end = min(len(text), keyword_pos + len(keyword) + 50)
        context = text[start:end]
        
        for pattern in self.price_patterns:
            matches = re.finditer(pattern, context)
            for match in matches:
                try:
                    price_str = match.group(1)
                    price = self._parse_price(price_str, pattern)
                    
                    if price and 1000 <= price <= 10000000:  # 1천원 ~ 1천만원
                        # 거리 기반 신뢰도 계산
                        distance = abs(match.start() - (keyword_pos - start))
                        confidence = max(0.5, 1.0 - (distance / 50))
                        prices.append((price, confidence))
                        
                except (ValueError, IndexError):
                    continue
        
        return prices
    
    def _parse_price(self, price_str: str, pattern: str) -> Optional[int]:
        """가격 문자열을 숫자로 변환"""
        try:
            if '만원' in pattern:
                return int(price_str) * 10000
            elif '천원' in pattern:
                return int(price_str) * 1000
            else:
                return int(price_str.replace(',', ''))
        except ValueError:
            return None