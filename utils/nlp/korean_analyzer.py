"""
한국어 형태소 분석기 및 텍스트 처리 유틸리티
"""
from typing import List, Dict, Tuple, Optional, Set
import re
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from collections import Counter

logger = logging.getLogger(__name__)

# KoNLPy 형태소 분석기들 (선택적 import)
try:
    from konlpy.tag import Okt, Mecab, Komoran, Hannanum
    KONLPY_AVAILABLE = True
except ImportError:
    logger.warning("KoNLPy가 설치되지 않았습니다. 기본 분석기를 사용합니다.")
    KONLPY_AVAILABLE = False


@dataclass
class Token:
    """토큰 정보"""
    text: str
    pos: str  # 품사
    start: int = 0
    end: int = 0


@dataclass
class AnalysisResult:
    """분석 결과"""
    original_text: str
    tokens: List[Token]
    nouns: List[str]
    adjectives: List[str]
    verbs: List[str]
    keywords: List[str]
    cleaned_text: str


class BaseKoreanAnalyzer(ABC):
    """한국어 분석기 기본 클래스"""
    
    def __init__(self):
        self.stopwords = self._load_stopwords()
        self.dental_keywords = self._load_dental_keywords()
    
    @abstractmethod
    def analyze(self, text: str) -> AnalysisResult:
        """텍스트 분석"""
        pass
    
    def _load_stopwords(self) -> Set[str]:
        """불용어 로드"""
        return {
            # 조사
            '이', '가', '을', '를', '에', '에서', '로', '으로', '와', '과', '의', '도', '만', '부터', '까지',
            # 어미
            '다', '요', '습니다', '입니다', '네요', '어요', '아요', '죠', '지요',
            # 대명사
            '이것', '그것', '저것', '여기', '거기', '저기', '이곳', '그곳', '저곳',
            # 부사
            '정말', '진짜', '너무', '매우', '아주', '완전', '조금', '좀', '많이', '잘', '못',
            # 감탄사
            '아', '어', '오', '우', '음', '흠', '헉', '와', '우와',
            # 기타
            '것', '거', '게', '걸', '건', '겁', '게요', '거예요', '거에요'
        }
    
    def _load_dental_keywords(self) -> Dict[str, List[str]]:
        """치과 관련 키워드 사전"""
        return {
            'treatment': [
                '스케일링', '임플란트', '신경치료', '근관치료', '교정', '미백', '발치', 
                '충치', '치료', '크라운', '브릿지', '틀니', '의치', '레진', '아말감',
                '사랑니', '치석', '잇몸', '치주', '보철', '보존', '구강외과'
            ],
            'symptoms': [
                '아픔', '아프다', '통증', '시림', '시리다', '붓기', '부었다', '출혈',
                '피', '냄새', '구취', '흔들림', '흔들리다', '깨짐', '깨졌다'
            ],
            'quality': [
                '친절', '불친절', '실력', '숙련', '경험', '전문', '정확', '꼼꼼',
                '대충', '성의', '성실', '불성실', '신중', '급하다'
            ],
            'facility': [
                '시설', '장비', '기계', '깨끗', '더럽다', '위생', '소독', '멸균',
                '최신', '구식', '낡은', '새로운', '현대적', '첨단'
            ],
            'service': [
                '서비스', '상담', '설명', '안내', '예약', '대기', '기다림', '빠르다',
                '느리다', '신속', '지연', '늦다', '시간', '정시', '지각'
            ],
            'price': [
                '가격', '비용', '돈', '비싸다', '싸다', '저렴', '합리적', '적정',
                '과도', '바가지', '할인', '이벤트', '보험', '급여', '비급여'
            ],
            'overtreatment': [
                '과잉진료', '과잉', '불필요', '억지', '강요', '권유', '추천',
                '필수', '선택', '옵션', '추가', '더', '많이'
            ]
        }
    
    def extract_keywords(self, tokens: List[Token], min_length: int = 2) -> List[str]:
        """키워드 추출"""
        keywords = []
        
        for token in tokens:
            # 명사, 형용사, 동사만 추출
            if token.pos in ['Noun', 'Adjective', 'Verb'] and len(token.text) >= min_length:
                if token.text not in self.stopwords:
                    keywords.append(token.text)
        
        # 빈도순 정렬
        keyword_counts = Counter(keywords)
        return [word for word, count in keyword_counts.most_common(20)]
    
    def categorize_keywords(self, keywords: List[str]) -> Dict[str, List[str]]:
        """키워드 카테고리 분류"""
        categorized = {category: [] for category in self.dental_keywords.keys()}
        
        for keyword in keywords:
            for category, category_keywords in self.dental_keywords.items():
                if any(ck in keyword for ck in category_keywords):
                    categorized[category].append(keyword)
                    break
        
        return categorized


class OktAnalyzer(BaseKoreanAnalyzer):
    """Okt(Open Korean Text) 기반 분석기"""
    
    def __init__(self):
        super().__init__()
        self.okt = None
        if KONLPY_AVAILABLE:
            try:
                self.okt = Okt()
                logger.info("Okt 분석기 초기화 성공")
            except Exception as e:
                logger.warning(f"Okt 분석기 초기화 실패: {e}")
                self.okt = None
        else:
            logger.warning("KoNLPy가 설치되지 않았습니다.")
    
    def analyze(self, text: str) -> AnalysisResult:
        """Okt를 사용한 텍스트 분석"""
        if not self.okt:
            return self._fallback_analyze(text)
        
        try:
            # 형태소 분석
            morphs = self.okt.pos(text, norm=True, stem=True)
            
            # 토큰 생성
            tokens = []
            nouns = []
            adjectives = []
            verbs = []
            
            for morph, pos in morphs:
                token = Token(text=morph, pos=pos)
                tokens.append(token)
                
                if pos == 'Noun':
                    nouns.append(morph)
                elif pos == 'Adjective':
                    adjectives.append(morph)
                elif pos == 'Verb':
                    verbs.append(morph)
            
            # 키워드 추출
            keywords = self.extract_keywords(tokens)
            
            # 텍스트 정제
            cleaned_text = ' '.join([token.text for token in tokens if token.pos in ['Noun', 'Adjective', 'Verb']])
            
            return AnalysisResult(
                original_text=text,
                tokens=tokens,
                nouns=nouns,
                adjectives=adjectives,
                verbs=verbs,
                keywords=keywords,
                cleaned_text=cleaned_text
            )
            
        except Exception as e:
            logger.error(f"Okt 분석 실패: {e}")
            return self._fallback_analyze(text)
    
    def _fallback_analyze(self, text: str) -> AnalysisResult:
        """폴백 분석 (KoNLPy 없을 때)"""
        # 간단한 공백 기반 토큰화
        words = text.split()
        tokens = [Token(text=word, pos='Unknown') for word in words]
        
        return AnalysisResult(
            original_text=text,
            tokens=tokens,
            nouns=words,
            adjectives=[],
            verbs=[],
            keywords=words[:10],
            cleaned_text=text
        )


class MecabAnalyzer(BaseKoreanAnalyzer):
    """Mecab 기반 분석기 (더 정확하지만 설치 복잡)"""
    
    def __init__(self):
        super().__init__()
        if KONLPY_AVAILABLE:
            try:
                self.mecab = Mecab()
            except Exception as e:
                logger.warning(f"Mecab 초기화 실패: {e}")
                self.mecab = None
        else:
            self.mecab = None
    
    def analyze(self, text: str) -> AnalysisResult:
        """Mecab을 사용한 텍스트 분석"""
        if not self.mecab:
            # Okt로 폴백
            return OktAnalyzer().analyze(text)
        
        try:
            # 형태소 분석
            morphs = self.mecab.pos(text)
            
            # 토큰 생성
            tokens = []
            nouns = []
            adjectives = []
            verbs = []
            
            for morph, pos in morphs:
                # Mecab 품사 태그를 단순화
                simplified_pos = self._simplify_pos(pos)
                token = Token(text=morph, pos=simplified_pos)
                tokens.append(token)
                
                if simplified_pos == 'Noun':
                    nouns.append(morph)
                elif simplified_pos == 'Adjective':
                    adjectives.append(morph)
                elif simplified_pos == 'Verb':
                    verbs.append(morph)
            
            # 키워드 추출
            keywords = self.extract_keywords(tokens)
            
            # 텍스트 정제
            cleaned_text = ' '.join([token.text for token in tokens if token.pos in ['Noun', 'Adjective', 'Verb']])
            
            return AnalysisResult(
                original_text=text,
                tokens=tokens,
                nouns=nouns,
                adjectives=adjectives,
                verbs=verbs,
                keywords=keywords,
                cleaned_text=cleaned_text
            )
            
        except Exception as e:
            logger.error(f"Mecab 분석 실패: {e}")
            return OktAnalyzer().analyze(text)
    
    def _simplify_pos(self, pos: str) -> str:
        """Mecab 품사 태그 단순화"""
        if pos.startswith('NN'):  # 명사
            return 'Noun'
        elif pos.startswith('VV') or pos.startswith('VA'):  # 동사, 형용사
            return 'Verb' if pos.startswith('VV') else 'Adjective'
        elif pos.startswith('JK') or pos.startswith('JX'):  # 조사
            return 'Josa'
        elif pos.startswith('EP') or pos.startswith('EF'):  # 어미
            return 'Eomi'
        else:
            return 'Other'


class KoreanAnalyzerManager:
    """한국어 분석기 관리자"""
    
    def __init__(self, preferred_analyzer: str = 'okt'):
        self.preferred_analyzer = preferred_analyzer
        self.analyzers = {
            'okt': OktAnalyzer(),
            'mecab': MecabAnalyzer()
        }
    
    def get_analyzer(self, analyzer_name: Optional[str] = None) -> BaseKoreanAnalyzer:
        """분석기 조회"""
        name = analyzer_name or self.preferred_analyzer
        return self.analyzers.get(name, self.analyzers['okt'])
    
    def analyze_text(self, text: str, analyzer_name: Optional[str] = None) -> AnalysisResult:
        """텍스트 분석"""
        analyzer = self.get_analyzer(analyzer_name)
        return analyzer.analyze(text)
    
    def batch_analyze(self, texts: List[str], analyzer_name: Optional[str] = None) -> List[AnalysisResult]:
        """일괄 텍스트 분석"""
        analyzer = self.get_analyzer(analyzer_name)
        results = []
        
        for text in texts:
            try:
                result = analyzer.analyze(text)
                results.append(result)
            except Exception as e:
                logger.error(f"텍스트 분석 실패: {text[:50]}... - {e}")
                # 빈 결과 추가
                results.append(AnalysisResult(
                    original_text=text,
                    tokens=[],
                    nouns=[],
                    adjectives=[],
                    verbs=[],
                    keywords=[],
                    cleaned_text=text
                ))
        
        return results


# 전역 분석기 매니저 인스턴스
korean_analyzer = KoreanAnalyzerManager()


def analyze_korean_text(text: str, analyzer: str = 'okt') -> AnalysisResult:
    """한국어 텍스트 분석 편의 함수"""
    return korean_analyzer.analyze_text(text, analyzer)


def extract_dental_aspects(text: str) -> Dict[str, List[str]]:
    """치과 관련 측면 추출"""
    result = analyze_korean_text(text)
    analyzer = korean_analyzer.get_analyzer()
    return analyzer.categorize_keywords(result.keywords)


def preprocess_for_ml(text: str, min_length: int = 2) -> str:
    """ML 모델용 텍스트 전처리"""
    result = analyze_korean_text(text)
    
    # 의미있는 단어만 추출
    meaningful_words = []
    for token in result.tokens:
        if (token.pos in ['Noun', 'Adjective', 'Verb'] and 
            len(token.text) >= min_length and 
            token.text not in korean_analyzer.get_analyzer().stopwords):
            meaningful_words.append(token.text)
    
    return ' '.join(meaningful_words)