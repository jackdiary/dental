"""
리뷰 텍스트 전처리 파이프라인
"""
from typing import List, Dict, Optional, Tuple
import re
import logging
from dataclasses import dataclass
from django.utils import timezone
from .korean_analyzer import korean_analyzer, AnalysisResult

logger = logging.getLogger(__name__)


@dataclass
class PreprocessingConfig:
    """전처리 설정"""
    remove_special_chars: bool = True
    normalize_whitespace: bool = True
    remove_short_words: bool = True
    min_word_length: int = 2
    remove_stopwords: bool = True
    extract_keywords: bool = True
    max_keywords: int = 20
    analyzer_type: str = 'okt'


@dataclass
class PreprocessedReview:
    """전처리된 리뷰 데이터"""
    original_text: str
    cleaned_text: str
    processed_text: str
    keywords: List[str]
    dental_aspects: Dict[str, List[str]]
    analysis_result: AnalysisResult
    metadata: Dict


class ReviewPreprocessor:
    """리뷰 전처리기"""
    
    def __init__(self, config: Optional[PreprocessingConfig] = None):
        self.config = config or PreprocessingConfig()
        self.analyzer = korean_analyzer
    
    def preprocess_single(self, text: str) -> PreprocessedReview:
        """단일 리뷰 전처리"""
        try:
            # 1단계: 기본 텍스트 정제
            cleaned_text = self._clean_text(text)
            
            # 2단계: 형태소 분석
            analysis_result = self.analyzer.analyze_text(
                cleaned_text, 
                self.config.analyzer_type
            )
            
            # 3단계: 처리된 텍스트 생성
            processed_text = self._generate_processed_text(analysis_result)
            
            # 4단계: 키워드 추출
            keywords = self._extract_keywords(analysis_result)
            
            # 5단계: 치과 관련 측면 추출
            dental_aspects = self._extract_dental_aspects(analysis_result)
            
            # 메타데이터 생성
            metadata = self._generate_metadata(text, analysis_result)
            
            return PreprocessedReview(
                original_text=text,
                cleaned_text=cleaned_text,
                processed_text=processed_text,
                keywords=keywords,
                dental_aspects=dental_aspects,
                analysis_result=analysis_result,
                metadata=metadata
            )
            
        except Exception as e:
            logger.error(f"리뷰 전처리 실패: {text[:50]}... - {e}")
            # 실패 시 기본 결과 반환
            return self._create_fallback_result(text)
    
    def preprocess_batch(self, texts: List[str]) -> List[PreprocessedReview]:
        """일괄 리뷰 전처리"""
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = self.preprocess_single(text)
                results.append(result)
                
                if (i + 1) % 100 == 0:
                    logger.info(f"전처리 진행: {i + 1}/{len(texts)}")
                    
            except Exception as e:
                logger.error(f"배치 전처리 실패 (인덱스 {i}): {e}")
                results.append(self._create_fallback_result(text))
        
        logger.info(f"일괄 전처리 완료: {len(results)}개")
        return results
    
    def _clean_text(self, text: str) -> str:
        """기본 텍스트 정제"""
        if not text:
            return ""
        
        cleaned = text
        
        if self.config.remove_special_chars:
            # 특수문자 제거 (한글, 영문, 숫자, 기본 문장부호만 유지)
            cleaned = re.sub(r'[^\w\s가-힣.,!?()[\]{}":;-]', ' ', cleaned)
        
        if self.config.normalize_whitespace:
            # 연속된 공백을 하나로 통일
            cleaned = re.sub(r'\s+', ' ', cleaned)
            cleaned = cleaned.strip()
        
        # HTML 태그 제거
        cleaned = re.sub(r'<[^>]+>', '', cleaned)
        
        # URL 제거
        cleaned = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', cleaned)
        
        # 이메일 제거 (이미 익명화되었지만 추가 보안)
        cleaned = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[이메일]', cleaned)
        
        # 전화번호 패턴 제거
        cleaned = re.sub(r'\b\d{2,3}[-\s]?\d{3,4}[-\s]?\d{4}\b', '[전화번호]', cleaned)
        
        return cleaned.strip()
    
    def _generate_processed_text(self, analysis_result: AnalysisResult) -> str:
        """처리된 텍스트 생성"""
        meaningful_tokens = []
        
        for token in analysis_result.tokens:
            # 의미있는 품사만 선택
            if token.pos in ['Noun', 'Adjective', 'Verb']:
                # 길이 필터링
                if self.config.remove_short_words and len(token.text) < self.config.min_word_length:
                    continue
                
                # 불용어 제거
                if self.config.remove_stopwords:
                    analyzer = self.analyzer.get_analyzer()
                    if token.text in analyzer.stopwords:
                        continue
                
                meaningful_tokens.append(token.text)
        
        return ' '.join(meaningful_tokens)
    
    def _extract_keywords(self, analysis_result: AnalysisResult) -> List[str]:
        """키워드 추출"""
        if not self.config.extract_keywords:
            return []
        
        # 분석 결과에서 키워드 가져오기
        keywords = analysis_result.keywords[:self.config.max_keywords]
        
        # 치과 관련 키워드 우선순위 부여
        dental_keywords = []
        general_keywords = []
        
        analyzer = self.analyzer.get_analyzer()
        all_dental_words = []
        for category_words in analyzer.dental_keywords.values():
            all_dental_words.extend(category_words)
        
        for keyword in keywords:
            if any(dental_word in keyword for dental_word in all_dental_words):
                dental_keywords.append(keyword)
            else:
                general_keywords.append(keyword)
        
        # 치과 키워드를 앞에 배치
        return dental_keywords + general_keywords
    
    def _extract_dental_aspects(self, analysis_result: AnalysisResult) -> Dict[str, List[str]]:
        """치과 관련 측면 추출"""
        analyzer = self.analyzer.get_analyzer()
        return analyzer.categorize_keywords(analysis_result.keywords)
    
    def _generate_metadata(self, original_text: str, analysis_result: AnalysisResult) -> Dict:
        """메타데이터 생성"""
        return {
            'original_length': len(original_text),
            'processed_length': len(analysis_result.cleaned_text),
            'token_count': len(analysis_result.tokens),
            'noun_count': len(analysis_result.nouns),
            'adjective_count': len(analysis_result.adjectives),
            'verb_count': len(analysis_result.verbs),
            'keyword_count': len(analysis_result.keywords),
            'processed_at': timezone.now().isoformat(),
            'analyzer_type': self.config.analyzer_type
        }
    
    def _create_fallback_result(self, text: str) -> PreprocessedReview:
        """실패 시 폴백 결과 생성"""
        cleaned = self._clean_text(text)
        
        return PreprocessedReview(
            original_text=text,
            cleaned_text=cleaned,
            processed_text=cleaned,
            keywords=[],
            dental_aspects={},
            analysis_result=AnalysisResult(
                original_text=text,
                tokens=[],
                nouns=[],
                adjectives=[],
                verbs=[],
                keywords=[],
                cleaned_text=cleaned
            ),
            metadata={
                'original_length': len(text),
                'processed_length': len(cleaned),
                'error': True,
                'processed_at': timezone.now().isoformat()
            }
        )


class ReviewPreprocessingPipeline:
    """리뷰 전처리 파이프라인"""
    
    def __init__(self, config: Optional[PreprocessingConfig] = None):
        self.preprocessor = ReviewPreprocessor(config)
        self.stats = {
            'total_processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'end_time': None
        }
    
    def process_reviews(self, reviews: List[str]) -> List[PreprocessedReview]:
        """리뷰 목록 전처리"""
        self.stats['start_time'] = timezone.now()
        self.stats['total_processed'] = len(reviews)
        
        logger.info(f"리뷰 전처리 파이프라인 시작: {len(reviews)}개")
        
        results = []
        
        for i, review_text in enumerate(reviews):
            try:
                result = self.preprocessor.preprocess_single(review_text)
                
                if result.metadata.get('error'):
                    self.stats['failed'] += 1
                else:
                    self.stats['successful'] += 1
                
                results.append(result)
                
                # 진행상황 로깅
                if (i + 1) % 50 == 0:
                    logger.info(f"전처리 진행: {i + 1}/{len(reviews)} ({((i + 1) / len(reviews) * 100):.1f}%)")
                    
            except Exception as e:
                logger.error(f"리뷰 전처리 실패 (인덱스 {i}): {e}")
                self.stats['failed'] += 1
                results.append(self.preprocessor._create_fallback_result(review_text))
        
        self.stats['end_time'] = timezone.now()
        self._log_statistics()
        
        return results
    
    def _log_statistics(self):
        """통계 로깅"""
        duration = (self.stats['end_time'] - self.stats['start_time']).total_seconds()
        success_rate = (self.stats['successful'] / self.stats['total_processed']) * 100 if self.stats['total_processed'] > 0 else 0
        
        logger.info(f"""
        전처리 파이프라인 완료:
        - 총 처리: {self.stats['total_processed']}개
        - 성공: {self.stats['successful']}개
        - 실패: {self.stats['failed']}개
        - 성공률: {success_rate:.1f}%
        - 소요시간: {duration:.2f}초
        - 처리속도: {self.stats['total_processed'] / duration:.1f}개/초
        """)


class TextQualityAnalyzer:
    """텍스트 품질 분석기"""
    
    @staticmethod
    def analyze_quality(text: str) -> Dict[str, float]:
        """텍스트 품질 분석"""
        if not text:
            return {'overall_score': 0.0}
        
        scores = {}
        
        # 길이 점수 (50-500자가 적정)
        length = len(text)
        if 50 <= length <= 500:
            scores['length_score'] = 1.0
        elif length < 50:
            scores['length_score'] = length / 50
        else:
            scores['length_score'] = max(0.5, 1.0 - (length - 500) / 1000)
        
        # 한글 비율 점수
        korean_chars = len(re.findall(r'[가-힣]', text))
        korean_ratio = korean_chars / length if length > 0 else 0
        scores['korean_ratio_score'] = min(1.0, korean_ratio * 2)  # 50% 이상이면 만점
        
        # 특수문자 비율 점수 (적을수록 좋음)
        special_chars = len(re.findall(r'[^\w\s가-힣.,!?()[\]{}":;-]', text))
        special_ratio = special_chars / length if length > 0 else 0
        scores['special_char_score'] = max(0.0, 1.0 - special_ratio * 5)
        
        # 반복 문자 점수 (과도한 반복 감지)
        repeated_chars = len(re.findall(r'(.)\1{3,}', text))  # 4번 이상 반복
        scores['repetition_score'] = max(0.0, 1.0 - repeated_chars * 0.2)
        
        # 의미있는 단어 비율
        try:
            analysis = korean_analyzer.analyze_text(text)
            meaningful_tokens = [t for t in analysis.tokens if t.pos in ['Noun', 'Adjective', 'Verb']]
            meaningful_ratio = len(meaningful_tokens) / len(analysis.tokens) if analysis.tokens else 0
            scores['meaningful_ratio_score'] = meaningful_ratio
        except Exception:
            scores['meaningful_ratio_score'] = 0.5  # 기본값
        
        # 전체 점수 계산 (가중평균)
        weights = {
            'length_score': 0.2,
            'korean_ratio_score': 0.2,
            'special_char_score': 0.2,
            'repetition_score': 0.2,
            'meaningful_ratio_score': 0.2
        }
        
        overall_score = sum(scores[key] * weights[key] for key in weights.keys())
        scores['overall_score'] = overall_score
        
        return scores
    
    @staticmethod
    def is_high_quality(text: str, threshold: float = 0.6) -> bool:
        """고품질 텍스트 여부 판단"""
        quality_scores = TextQualityAnalyzer.analyze_quality(text)
        return quality_scores['overall_score'] >= threshold


# 전역 전처리기 인스턴스
default_preprocessor = ReviewPreprocessor()
default_pipeline = ReviewPreprocessingPipeline()


def preprocess_review_text(text: str, config: Optional[PreprocessingConfig] = None) -> PreprocessedReview:
    """리뷰 텍스트 전처리 편의 함수"""
    if config:
        preprocessor = ReviewPreprocessor(config)
        return preprocessor.preprocess_single(text)
    else:
        return default_preprocessor.preprocess_single(text)


def batch_preprocess_reviews(texts: List[str], config: Optional[PreprocessingConfig] = None) -> List[PreprocessedReview]:
    """일괄 리뷰 전처리 편의 함수"""
    if config:
        pipeline = ReviewPreprocessingPipeline(config)
        return pipeline.process_reviews(texts)
    else:
        return default_pipeline.process_reviews(texts)
class 
TextPreprocessor:
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
        
        return tex