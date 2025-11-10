"""
Text processing utilities for Korean language
"""
import re
import hashlib
from typing import List, Optional


def anonymize_personal_info(text: str) -> str:
    """
    개인정보 익명화 함수
    """
    # 전화번호 패턴 (010-1234-5678, 02-123-4567 등)
    phone_pattern = r'(\d{2,3}[-\s]?\d{3,4}[-\s]?\d{4})'
    text = re.sub(phone_pattern, '[전화번호]', text)
    
    # 이메일 패턴
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    text = re.sub(email_pattern, '[이메일]', text)
    
    # 주민등록번호 패턴 (앞 6자리만)
    ssn_pattern = r'\d{6}[-\s]?\d{7}'
    text = re.sub(ssn_pattern, '[주민번호]', text)
    
    return text


def create_reviewer_hash(reviewer_name: str, review_date: str = None) -> str:
    """
    리뷰어 익명화를 위한 해시 생성
    """
    if not reviewer_name:
        return ''
    
    # 리뷰어 이름과 날짜를 조합하여 해시 생성
    hash_input = f"{reviewer_name}_{review_date or ''}"
    return hashlib.sha256(hash_input.encode('utf-8')).hexdigest()


def clean_text(text: str) -> str:
    """
    텍스트 정제 함수
    """
    if not text:
        return ''
    
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', '', text)
    
    # 특수문자 정리 (한글, 영문, 숫자, 기본 문장부호만 유지)
    text = re.sub(r'[^\w\s가-힣.,!?()[\]{}":;-]', '', text)
    
    # 연속된 공백 정리
    text = re.sub(r'\s+', ' ', text)
    
    # 앞뒤 공백 제거
    text = text.strip()
    
    return text


def extract_keywords(text: str, min_length: int = 2) -> List[str]:
    """
    텍스트에서 키워드 추출 (기본적인 방법)
    """
    if not text:
        return []
    
    # 단어 분리 (공백 기준)
    words = text.split()
    
    # 길이 필터링 및 정리
    keywords = []
    for word in words:
        # 특수문자 제거
        clean_word = re.sub(r'[^\w가-힣]', '', word)
        if len(clean_word) >= min_length:
            keywords.append(clean_word)
    
    return list(set(keywords))  # 중복 제거


def is_korean_text(text: str) -> bool:
    """
    한글 텍스트 여부 확인
    """
    if not text:
        return False
    
    korean_chars = re.findall(r'[가-힣]', text)
    return len(korean_chars) > len(text) * 0.3  # 30% 이상이 한글이면 한글 텍스트로 판단


# 불용어 리스트 (기본적인 것들)
KOREAN_STOPWORDS = {
    '그리고', '그런데', '하지만', '그러나', '또한', '또', '그래서', '따라서',
    '이것', '그것', '저것', '이거', '그거', '저거', '이런', '그런', '저런',
    '여기', '거기', '저기', '이곳', '그곳', '저곳', '이때', '그때', '저때',
    '오늘', '어제', '내일', '지금', '나중에', '먼저', '다음', '마지막',
    '정말', '진짜', '너무', '매우', '아주', '완전', '조금', '좀', '많이',
    '있다', '없다', '되다', '하다', '이다', '아니다', '같다', '다르다'
}


def remove_stopwords(words: List[str]) -> List[str]:
    """
    불용어 제거
    """
    return [word for word in words if word not in KOREAN_STOPWORDS]