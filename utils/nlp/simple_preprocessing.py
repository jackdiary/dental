"""
간단한 텍스트 전처리기
"""
import re

class TextPreprocessor:
    """간단한 텍스트 전처리기"""
    
    def __init__(self):
        # 불용어 리스트
        self.stopwords = [
            '이', '그', '저', '것', '수', '있', '없', '하', '되', '된', '될', '한', '할',
            '했', '해', '하는', '하고', '하지', '하면', '하여', '하니', '하게', '하자',
            '의', '가', '이', '을', '를', '에', '와', '과', '도', '만', '부터', '까지',
            '으로', '로', '에서', '에게', '께', '한테', '보고', '더', '가장', '매우',
            '너무', '정말', '진짜', '아주', '완전', '엄청', '되게', '좀', '조금'
        ]
    
    def preprocess(self, text: str) -> str:
        """텍스트 전처리"""
        if not text:
            return ""
        
        # 기본 정제
        cleaned = self._clean_text(text)
        
        # 토큰화 및 불용어 제거 (간단 버전)
        tokens = cleaned.split()
        filtered_tokens = [
            token for token in tokens 
            if len(token) > 1 and token not in self.stopwords
        ]
        
        return ' '.join(filtered_tokens)
    
    def _clean_text(self, text: str) -> str:
        """기본 텍스트 정제"""
        # 특수문자 제거 (한글, 영문, 숫자, 공백만 유지)
        text = re.sub(r'[^\w\s가-힣]', ' ', text)
        
        # 연속된 공백을 하나로
        text = re.sub(r'\s+', ' ', text)
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        return text