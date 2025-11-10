"""
Aspect-Based Sentiment Analysis (ABSA) 엔진
치과 리뷰의 6가지 측면별 감성 분석
"""
from typing import Dict, List, Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
import re
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)

# scikit-learn 선택적 import
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.svm import SVC
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    logger.warning("scikit-learn이 설치되지 않았습니다. 기본 감성 분석기를 사용합니다.")
    SKLEARN_AVAILABLE = False


@dataclass
class AspectScores:
    """측면별 감성 점수"""
    price_score: float = 0.0          # 가격 점수 (-1 ~ +1)
    skill_score: float = 0.0          # 실력 점수 (-1 ~ +1)
    kindness_score: float = 0.0       # 친절도 점수 (-1 ~ +1)
    waiting_time_score: float = 0.0   # 대기시간 점수 (-1 ~ +1)
    facility_score: float = 0.0       # 시설 점수 (-1 ~ +1)
    overtreatment_score: float = 0.0  # 과잉진료 점수 (-1 ~ +1)
    
    def to_dict(self) -> Dict[str, float]:
        """딕셔너리로 변환"""
        return {
            'price_score': self.price_score,
            'skill_score': self.skill_score,
            'kindness_score': self.kindness_score,
            'waiting_time_score': self.waiting_time_score,
            'facility_score': self.facility_score,
            'overtreatment_score': self.overtreatment_score
        }
    
    def get_overall_score(self) -> float:
        """전체 평균 점수"""
        scores = [
            self.price_score, self.skill_score, self.kindness_score,
            self.waiting_time_score, self.facility_score, self.overtreatment_score
        ]
        return sum(scores) / len(scores)


class SentimentAnalyzer:
    """간단한 감성 분석기"""
    
    def __init__(self):
        # 측면별 키워드 사전
        self.aspect_keywords = {
            'price': {
                'positive': ['저렴', '합리적', '싸', '가성비', '적당', '괜찮'],
                'negative': ['비싸', '비쌈', '돈', '부담', '과도', '바가지']
            },
            'skill': {
                'positive': ['실력', '잘해', '꼼꼼', '정확', '전문', '능숙', '훌륭'],
                'negative': ['서툴', '못해', '실수', '부정확', '미숙']
            },
            'kindness': {
                'positive': ['친절', '상냥', '따뜻', '배려', '정성', '세심'],
                'negative': ['불친절', '차갑', '무뚝뚝', '성의없', '대충']
            },
            'waiting_time': {
                'positive': ['빨리', '신속', '즉시', '바로', '대기없이'],
                'negative': ['오래', '늦', '기다림', '대기', '지연']
            },
            'facility': {
                'positive': ['깨끗', '시설좋', '현대적', '쾌적', '넓'],
                'negative': ['더럽', '낡', '좁', '불편', '시설나쁨']
            },
            'overtreatment': {
                'positive': ['필요한것만', '과잉없이', '정직', '양심적'],
                'negative': ['과잉', '불필요', '강요', '과도한']
            }
        }
    
    def analyze_aspects(self, text: str) -> Dict[str, float]:
        """측면별 감성 분석"""
        scores = {}
        
        for aspect, keywords in self.aspect_keywords.items():
            positive_count = 0
            negative_count = 0
            
            # 긍정 키워드 카운트
            for keyword in keywords['positive']:
                positive_count += text.count(keyword)
            
            # 부정 키워드 카운트
            for keyword in keywords['negative']:
                negative_count += text.count(keyword)
            
            # 점수 계산 (-1 ~ +1)
            total_count = positive_count + negative_count
            if total_count > 0:
                score = (positive_count - negative_count) / total_count
            else:
                score = 0.0
            
            scores[aspect] = max(-1.0, min(1.0, score))
        
        return scores
        scores = [
            self.price_score, self.skill_score, self.kindness_score,
            self.waiting_time_score, self.facility_score, self.overtreatment_score
        ]
        return sum(scores) / len(scores)


@dataclass
class SentimentResult:
    """감성 분석 결과"""
    text: str
    aspect_scores: AspectScores
    confidence: float
    detected_aspects: List[str]
    sentiment_words: Dict[str, List[str]]
    model_version: str = "1.0"


class BaseABSAEngine(ABC):
    """ABSA 엔진 기본 클래스"""
    
    def __init__(self):
        self.aspect_keywords = self._load_aspect_keywords()
        self.sentiment_lexicon = self._load_sentiment_lexicon()
    
    @abstractmethod
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """감성 분석 수행"""
        pass
    
    def _load_aspect_keywords(self) -> Dict[str, List[str]]:
        """측면별 키워드 사전"""
        return {
            'price': [
                '가격', '비용', '돈', '비싸다', '싸다', '저렴', '합리적', '적정',
                '과도', '바가지', '할인', '이벤트', '보험', '급여', '비급여',
                '만원', '천원', '원', '수가', '진료비', '치료비'
            ],
            'skill': [
                '실력', '숙련', '경험', '전문', '정확', '꼼꼼', '대충', '성의',
                '성실', '불성실', '신중', '급하다', '의사', '선생님', '원장',
                '기술', '솜씨', '능력', '전문성', '노하우'
            ],
            'kindness': [
                '친절', '불친절', '상냥', '무뚝뚝', '따뜻', '차갑다', '웃음',
                '미소', '인사', '말투', '태도', '서비스', '응대', '배려',
                '예의', '무례', '정중', '불쾌', '기분'
            ],
            'waiting_time': [
                '대기', '기다림', '빠르다', '느리다', '신속', '지연', '늦다',
                '시간', '정시', '지각', '예약', '순서', '대기실', '기다리다',
                '오래', '금방', '즉시', '바로'
            ],
            'facility': [
                '시설', '장비', '기계', '깨끗', '더럽다', '위생', '소독', '멸균',
                '최신', '구식', '낡은', '새로운', '현대적', '첨단', '환경',
                '인테리어', '건물', '병원', '의자', '도구'
            ],
            'overtreatment': [
                '과잉진료', '과잉', '불필요', '억지', '강요', '권유', '추천',
                '필수', '선택', '옵션', '추가', '더', '많이', '과도',
                '적당', '적절', '필요', '꼭', '반드시'
            ]
        }
    
    def _load_sentiment_lexicon(self) -> Dict[str, Dict[str, float]]:
        """감성 어휘 사전"""
        return {
            'positive': {
                # 일반 긍정어
                '좋다': 0.8, '훌륭하다': 0.9, '만족': 0.8, '추천': 0.7,
                '친절': 0.8, '깨끗': 0.7, '빠르다': 0.6, '정확': 0.7,
                '꼼꼼': 0.7, '신중': 0.6, '전문적': 0.8, '숙련': 0.7,
                '합리적': 0.7, '저렴': 0.6, '적정': 0.6, '괜찮다': 0.5,
                '최고': 0.9, '완벽': 0.9, '감사': 0.7, '고맙다': 0.7,
                
                # 치과 특화 긍정어
                '아프지않다': 0.8, '무통': 0.8, '편안': 0.7, '안전': 0.7,
                '깔끔': 0.7, '정성': 0.8, '세심': 0.7, '신속': 0.6,
                '효과적': 0.7, '성공적': 0.8, '개선': 0.6, '나아지다': 0.7
            },
            'negative': {
                # 일반 부정어
                '나쁘다': -0.8, '최악': -0.9, '불만': -0.8, '실망': -0.7,
                '불친절': -0.8, '더럽다': -0.7, '느리다': -0.6, '부정확': -0.7,
                '대충': -0.7, '급하다': -0.6, '비전문적': -0.8, '미숙': -0.7,
                '비싸다': -0.6, '과도': -0.7, '바가지': -0.8, '별로': -0.5,
                '화나다': -0.8, '짜증': -0.7, '후회': -0.7, '속상': -0.6,
                
                # 치과 특화 부정어
                '아프다': -0.7, '고통': -0.8, '불편': -0.6, '위험': -0.8,
                '지저분': -0.7, '불성실': -0.7, '무성의': -0.8, '지연': -0.6,
                '비효과적': -0.7, '실패': -0.8, '악화': -0.8, '나빠지다': -0.7,
                '과잉진료': -0.9, '강요': -0.8, '억지': -0.8, '불필요': -0.7
            }
        }
    
    def extract_aspect_mentions(self, text: str) -> Dict[str, List[str]]:
        """텍스트에서 측면별 언급 추출"""
        mentions = defaultdict(list)
        
        for aspect, keywords in self.aspect_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    mentions[aspect].append(keyword)
        
        return dict(mentions)
    
    def calculate_aspect_sentiment(self, text: str, aspect: str) -> Tuple[float, List[str]]:
        """특정 측면의 감성 점수 계산"""
        aspect_keywords = self.aspect_keywords.get(aspect, [])
        sentiment_words = []
        scores = []
        
        # 측면 관련 문장 추출
        sentences = re.split(r'[.!?]', text)
        relevant_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in aspect_keywords):
                relevant_sentences.append(sentence)
        
        if not relevant_sentences:
            return 0.0, []
        
        # 각 문장에서 감성 점수 계산
        for sentence in relevant_sentences:
            sentence_score, words = self._calculate_sentence_sentiment(sentence)
            if sentence_score != 0:
                scores.append(sentence_score)
                sentiment_words.extend(words)
        
        # 평균 점수 계산
        if scores:
            avg_score = sum(scores) / len(scores)
            # -1 ~ +1 범위로 정규화
            normalized_score = max(-1.0, min(1.0, avg_score))
            return normalized_score, sentiment_words
        
        return 0.0, []
    
    def _calculate_sentence_sentiment(self, sentence: str) -> Tuple[float, List[str]]:
        """문장의 감성 점수 계산"""
        positive_score = 0.0
        negative_score = 0.0
        found_words = []
        
        # 긍정어 검사
        for word, score in self.sentiment_lexicon['positive'].items():
            if word in sentence:
                positive_score += score
                found_words.append(f"+{word}")
        
        # 부정어 검사
        for word, score in self.sentiment_lexicon['negative'].items():
            if word in sentence:
                negative_score += abs(score)  # 절댓값으로 변환
                found_words.append(f"-{word}")
        
        # 부정 표현 검사 (안, 못, 없다 등)
        negation_patterns = ['안 ', '못 ', '없다', '아니다', '말다']
        has_negation = any(pattern in sentence for pattern in negation_patterns)
        
        if has_negation:
            # 부정 표현이 있으면 점수 반전
            total_score = -(positive_score - negative_score)
        else:
            total_score = positive_score - negative_score
        
        return total_score, found_words


class RuleBasedABSAEngine(BaseABSAEngine):
    """규칙 기반 ABSA 엔진"""
    
    def __init__(self):
        super().__init__()
        self.model_version = "rule_based_1.0"
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """규칙 기반 감성 분석"""
        try:
            # 각 측면별 감성 점수 계산
            price_score, price_words = self.calculate_aspect_sentiment(text, 'price')
            skill_score, skill_words = self.calculate_aspect_sentiment(text, 'skill')
            kindness_score, kindness_words = self.calculate_aspect_sentiment(text, 'kindness')
            waiting_score, waiting_words = self.calculate_aspect_sentiment(text, 'waiting_time')
            facility_score, facility_words = self.calculate_aspect_sentiment(text, 'facility')
            overtreatment_score, overtreatment_words = self.calculate_aspect_sentiment(text, 'overtreatment')
            
            # 측면 점수 객체 생성
            aspect_scores = AspectScores(
                price_score=price_score,
                skill_score=skill_score,
                kindness_score=kindness_score,
                waiting_time_score=waiting_score,
                facility_score=facility_score,
                overtreatment_score=overtreatment_score
            )
            
            # 감지된 측면 목록
            detected_aspects = []
            if price_score != 0: detected_aspects.append('price')
            if skill_score != 0: detected_aspects.append('skill')
            if kindness_score != 0: detected_aspects.append('kindness')
            if waiting_score != 0: detected_aspects.append('waiting_time')
            if facility_score != 0: detected_aspects.append('facility')
            if overtreatment_score != 0: detected_aspects.append('overtreatment')
            
            # 감성 단어 정리
            sentiment_words = {
                'price': price_words,
                'skill': skill_words,
                'kindness': kindness_words,
                'waiting_time': waiting_words,
                'facility': facility_words,
                'overtreatment': overtreatment_words
            }
            
            # 신뢰도 계산 (감지된 측면 수와 감성 단어 수 기반)
            confidence = min(1.0, (len(detected_aspects) * 0.2) + 
                           (sum(len(words) for words in sentiment_words.values()) * 0.1))
            
            return SentimentResult(
                text=text,
                aspect_scores=aspect_scores,
                confidence=confidence,
                detected_aspects=detected_aspects,
                sentiment_words=sentiment_words,
                model_version=self.model_version
            )
            
        except Exception as e:
            logger.error(f"감성 분석 실패: {e}")
            return self._create_fallback_result(text)
    
    def _create_fallback_result(self, text: str) -> SentimentResult:
        """실패 시 기본 결과 생성"""
        return SentimentResult(
            text=text,
            aspect_scores=AspectScores(),
            confidence=0.0,
            detected_aspects=[],
            sentiment_words={},
            model_version=self.model_version
        )


class MLBasedABSAEngine(BaseABSAEngine):
    """머신러닝 기반 ABSA 엔진 (향후 구현)"""
    
    def __init__(self):
        super().__init__()
        self.model_version = "ml_based_1.0"
        self.models = {}
        self.vectorizers = {}
        
        if SKLEARN_AVAILABLE:
            self._initialize_models()
        else:
            logger.warning("scikit-learn이 없어 ML 기반 분석기를 사용할 수 없습니다.")
    
    def _initialize_models(self):
        """ML 모델 초기화"""
        # 각 측면별로 별도의 분류기 생성
        aspects = ['price', 'skill', 'kindness', 'waiting_time', 'facility', 'overtreatment']
        
        for aspect in aspects:
            # TF-IDF + SVM 파이프라인
            self.models[aspect] = Pipeline([
                ('tfidf', TfidfVectorizer(max_features=1000, ngram_range=(1, 2))),
                ('svm', SVC(kernel='rbf', probability=True, random_state=42))
            ])
    
    def analyze_sentiment(self, text: str) -> SentimentResult:
        """ML 기반 감성 분석"""
        if not SKLEARN_AVAILABLE or not self.models:
            # 규칙 기반으로 폴백
            rule_engine = RuleBasedABSAEngine()
            return rule_engine.analyze_sentiment(text)
        
        # TODO: 실제 ML 모델 구현
        # 현재는 규칙 기반으로 폴백
        rule_engine = RuleBasedABSAEngine()
        result = rule_engine.analyze_sentiment(text)
        result.model_version = self.model_version
        return result


class ABSAEngineManager:
    """ABSA 엔진 관리자"""
    
    def __init__(self, default_engine: str = 'bert'):
        self.engines = {
            'rule_based': RuleBasedABSAEngine(),
            'ml_based': MLBasedABSAEngine(),
            'bert': self._get_bert_engine(),
            'kobert': self._get_kobert_engine()
        }
        self.default_engine = default_engine
    
    def _get_bert_engine(self):
        """BERT 엔진 조회"""
        try:
            from .bert_sentiment_analyzer import BertSentimentAnalyzer
            return BertSentimentAnalyzer()
        except ImportError:
            logger.warning("BERT 분석기를 사용할 수 없습니다. 규칙 기반으로 폴백합니다.")
            return RuleBasedABSAEngine()
    
    def _get_kobert_engine(self):
        """KoBERT 엔진 조회"""
        try:
            from .bert_sentiment_analyzer import KoBertSentimentAnalyzer
            return KoBertSentimentAnalyzer()
        except ImportError:
            logger.warning("KoBERT 분석기를 사용할 수 없습니다. 규칙 기반으로 폴백합니다.")
            return RuleBasedABSAEngine()
    
    def get_engine(self, engine_name: Optional[str] = None) -> BaseABSAEngine:
        """엔진 조회"""
        name = engine_name or self.default_engine
        return self.engines.get(name, self.engines['rule_based'])
    
    def analyze_sentiment(self, text: str, engine_name: Optional[str] = None) -> SentimentResult:
        """감성 분석 수행"""
        engine = self.get_engine(engine_name)
        return engine.analyze_sentiment(text)
    
    def batch_analyze(self, texts: List[str], engine_name: Optional[str] = None) -> List[SentimentResult]:
        """일괄 감성 분석"""
        engine = self.get_engine(engine_name)
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = engine.analyze_sentiment(text)
                results.append(result)
                
                if (i + 1) % 50 == 0:
                    logger.info(f"감성 분석 진행: {i + 1}/{len(texts)}")
                    
            except Exception as e:
                logger.error(f"감성 분석 실패 (인덱스 {i}): {e}")
                results.append(engine._create_fallback_result(text))
        
        return results


# 전역 ABSA 엔진 매니저
absa_manager = ABSAEngineManager()


def analyze_review_sentiment(text: str, engine: str = 'rule_based') -> SentimentResult:
    """리뷰 감성 분석 편의 함수"""
    return absa_manager.analyze_sentiment(text, engine)


def batch_analyze_sentiments(texts: List[str], engine: str = 'rule_based') -> List[SentimentResult]:
    """일괄 감성 분석 편의 함수"""
    return absa_manager.batch_analyze(texts, engine)