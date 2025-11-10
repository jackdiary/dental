"""
BERT/KoBERT 기반 딥러닝 감성 분석기
"""
import os
import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel, pipeline
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import json

logger = logging.getLogger(__name__)

# 선택적 import
try:
    from transformers import BertTokenizer, BertModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("transformers 라이브러리가 설치되지 않았습니다. pip install transformers torch 실행하세요.")
    TRANSFORMERS_AVAILABLE = False


@dataclass
class BertSentimentResult:
    """BERT 감성 분석 결과"""
    text: str
    aspect_scores: Dict[str, float]
    confidence: float
    embeddings: Optional[np.ndarray] = None
    attention_weights: Optional[Dict[str, float]] = None
    model_version: str = "bert_v1.0"


class AspectBasedBertAnalyzer:
    """측면 기반 BERT 감성 분석기"""
    
    def __init__(self, model_name: str = "klue/bert-base"):
        self.model_name = model_name
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.tokenizer = None
        self.model = None
        self.aspect_classifiers = {}
        
        # 치과 측면별 키워드 임베딩
        self.aspect_keywords = {
            'price': ['가격', '비용', '돈', '비싸다', '싸다', '저렴', '합리적', '바가지', '할인'],
            'skill': ['실력', '숙련', '경험', '전문', '정확', '꼼꼼', '대충', '미숙', '능숙'],
            'kindness': ['친절', '불친절', '상냥', '무뚝뚝', '따뜻', '차갑다', '예의', '무례'],
            'waiting_time': ['대기', '기다림', '빠르다', '느리다', '신속', '지연', '늦다', '정시'],
            'facility': ['시설', '장비', '깨끗', '더럽다', '위생', '소독', '최신', '낡은'],
            'overtreatment': ['과잉진료', '과잉', '불필요', '억지', '강요', '적절', '필요']
        }
        
        if TRANSFORMERS_AVAILABLE:
            self._initialize_model()
        else:
            logger.error("BERT 모델을 사용할 수 없습니다. transformers 라이브러리를 설치하세요.")
    
    def _initialize_model(self):
        """BERT 모델 초기화"""
        try:
            logger.info(f"BERT 모델 로딩 중: {self.model_name}")
            
            # 토크나이저와 모델 로드
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModel.from_pretrained(self.model_name)
            self.model.to(self.device)
            self.model.eval()
            
            # 감성 분석 파이프라인 (한국어)
            try:
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="beomi/KcELECTRA-base-v2022",
                    tokenizer="beomi/KcELECTRA-base-v2022",
                    device=0 if torch.cuda.is_available() else -1
                )
            except:
                # 폴백: 기본 다국어 모델
                self.sentiment_pipeline = pipeline(
                    "sentiment-analysis",
                    model="cardiffnlp/twitter-roberta-base-sentiment-latest",
                    device=0 if torch.cuda.is_available() else -1
                )
            
            # 측면별 키워드 임베딩 생성
            self._create_aspect_embeddings()
            
            logger.info("✅ BERT 모델 초기화 완료")
            
        except Exception as e:
            logger.error(f"❌ BERT 모델 초기화 실패: {e}")
            self.tokenizer = None
            self.model = None
    
    def _create_aspect_embeddings(self):
        """측면별 키워드 임베딩 생성"""
        self.aspect_embeddings = {}
        
        for aspect, keywords in self.aspect_keywords.items():
            embeddings = []
            
            for keyword in keywords:
                try:
                    embedding = self._get_word_embedding(keyword)
                    if embedding is not None:
                        embeddings.append(embedding)
                except Exception as e:
                    logger.warning(f"키워드 '{keyword}' 임베딩 실패: {e}")
            
            if embeddings:
                # 키워드들의 평균 임베딩
                self.aspect_embeddings[aspect] = np.mean(embeddings, axis=0)
                logger.info(f"✅ {aspect} 측면 임베딩 생성 완료 ({len(embeddings)}개 키워드)")
    
    def _get_word_embedding(self, word: str) -> Optional[np.ndarray]:
        """단어의 BERT 임베딩 추출"""
        if not self.tokenizer or not self.model:
            return None
        
        try:
            # 토큰화
            inputs = self.tokenizer(word, return_tensors="pt", padding=True, truncation=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # BERT 임베딩 추출
            with torch.no_grad():
                outputs = self.model(**inputs)
                # [CLS] 토큰의 임베딩 사용
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                return embedding.squeeze()
                
        except Exception as e:
            logger.error(f"단어 임베딩 추출 실패 '{word}': {e}")
            return None
    
    def _get_sentence_embedding(self, text: str) -> Optional[np.ndarray]:
        """문장의 BERT 임베딩 추출"""
        if not self.tokenizer or not self.model:
            return None
        
        try:
            # 토큰화 (최대 512 토큰)
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # BERT 임베딩 추출
            with torch.no_grad():
                outputs = self.model(**inputs)
                # [CLS] 토큰의 임베딩 사용 (문장 전체 표현)
                embedding = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                return embedding.squeeze()
                
        except Exception as e:
            logger.error(f"문장 임베딩 추출 실패: {e}")
            return None
    
    def analyze_sentiment(self, text: str) -> BertSentimentResult:
        """BERT 기반 측면별 감성 분석"""
        if not TRANSFORMERS_AVAILABLE or not self.model:
            return self._fallback_analysis(text)
        
        try:
            # 1. 전체 문장 임베딩
            sentence_embedding = self._get_sentence_embedding(text)
            
            # 2. 측면별 감성 점수 계산
            aspect_scores = {}
            attention_weights = {}
            
            for aspect in self.aspect_keywords.keys():
                score, attention = self._calculate_aspect_sentiment(text, aspect, sentence_embedding)
                aspect_scores[aspect] = score
                attention_weights[aspect] = attention
            
            # 3. 전체 감성 분석 (파이프라인 사용)
            try:
                sentiment_result = self.sentiment_pipeline(text)[0]
                confidence = sentiment_result['score']
            except:
                confidence = 0.7  # 기본값
            
            return BertSentimentResult(
                text=text,
                aspect_scores=aspect_scores,
                confidence=confidence,
                embeddings=sentence_embedding,
                attention_weights=attention_weights,
                model_version=f"bert_{self.model_name}_v1.0"
            )
            
        except Exception as e:
            logger.error(f"BERT 감성 분석 실패: {e}")
            return self._fallback_analysis(text)
    
    def _calculate_aspect_sentiment(
        self, 
        text: str, 
        aspect: str, 
        sentence_embedding: Optional[np.ndarray]
    ) -> Tuple[float, float]:
        """특정 측면의 감성 점수 계산"""
        try:
            # 1. 키워드 기반 점수
            keyword_score = self._keyword_based_score(text, aspect)
            
            # 2. 임베딩 기반 유사도 점수
            similarity_score = 0.0
            if sentence_embedding is not None and aspect in self.aspect_embeddings:
                aspect_embedding = self.aspect_embeddings[aspect]
                similarity = cosine_similarity(
                    sentence_embedding.reshape(1, -1),
                    aspect_embedding.reshape(1, -1)
                )[0][0]
                similarity_score = similarity
            
            # 3. 감성 파이프라인 점수
            sentiment_score = 0.0
            try:
                # 측면 관련 문장만 추출
                aspect_sentences = self._extract_aspect_sentences(text, aspect)
                if aspect_sentences:
                    sentiment_results = self.sentiment_pipeline(aspect_sentences)
                    for result in sentiment_results:
                        if result['label'] in ['POSITIVE', 'POS', '1']:
                            sentiment_score += result['score']
                        else:
                            sentiment_score -= result['score']
                    sentiment_score /= len(sentiment_results)
            except:
                pass
            
            # 4. 가중 평균 계산
            final_score = (
                keyword_score * 0.4 +
                similarity_score * 0.3 +
                sentiment_score * 0.3
            )
            
            # -1 ~ +1 범위로 정규화
            final_score = max(-1.0, min(1.0, final_score))
            
            # 어텐션 가중치 (유사도 기반)
            attention_weight = abs(similarity_score) if similarity_score else 0.1
            
            return final_score, attention_weight
            
        except Exception as e:
            logger.error(f"측면 감성 계산 실패 ({aspect}): {e}")
            return 0.0, 0.1
    
    def _keyword_based_score(self, text: str, aspect: str) -> float:
        """키워드 기반 감성 점수"""
        keywords = self.aspect_keywords.get(aspect, [])
        
        positive_keywords = {
            'price': ['저렴', '합리적', '싸다', '할인', '적정'],
            'skill': ['실력', '숙련', '경험', '전문', '정확', '꼼꼼', '능숙'],
            'kindness': ['친절', '상냥', '따뜻', '예의', '정중'],
            'waiting_time': ['빠르다', '신속', '정시', '즉시'],
            'facility': ['깨끗', '위생', '소독', '최신', '현대적'],
            'overtreatment': ['적절', '필요', '정직', '양심적']
        }
        
        negative_keywords = {
            'price': ['비싸다', '바가지', '과도', '부담'],
            'skill': ['대충', '미숙', '부정확', '서툴'],
            'kindness': ['불친절', '무뚝뚝', '차갑다', '무례'],
            'waiting_time': ['느리다', '지연', '늦다', '오래'],
            'facility': ['더럽다', '낡은', '구식', '불편'],
            'overtreatment': ['과잉진료', '과잉', '불필요', '억지', '강요']
        }
        
        pos_count = sum(1 for word in positive_keywords.get(aspect, []) if word in text)
        neg_count = sum(1 for word in negative_keywords.get(aspect, []) if word in text)
        
        if pos_count + neg_count == 0:
            return 0.0
        
        return (pos_count - neg_count) / (pos_count + neg_count)
    
    def _extract_aspect_sentences(self, text: str, aspect: str) -> List[str]:
        """측면 관련 문장 추출"""
        import re
        
        sentences = re.split(r'[.!?]', text)
        aspect_sentences = []
        keywords = self.aspect_keywords.get(aspect, [])
        
        for sentence in sentences:
            if any(keyword in sentence for keyword in keywords):
                aspect_sentences.append(sentence.strip())
        
        return aspect_sentences[:3]  # 최대 3개 문장
    
    def _fallback_analysis(self, text: str) -> BertSentimentResult:
        """폴백 분석 (BERT 사용 불가시)"""
        # 간단한 키워드 기반 분석
        aspect_scores = {}
        
        for aspect in self.aspect_keywords.keys():
            score = self._keyword_based_score(text, aspect)
            aspect_scores[aspect] = score
        
        return BertSentimentResult(
            text=text,
            aspect_scores=aspect_scores,
            confidence=0.5,
            model_version="fallback_v1.0"
        )
    
    def batch_analyze(self, texts: List[str]) -> List[BertSentimentResult]:
        """일괄 감성 분석"""
        results = []
        
        for i, text in enumerate(texts):
            try:
                result = self.analyze_sentiment(text)
                results.append(result)
                
                if (i + 1) % 10 == 0:
                    logger.info(f"BERT 분석 진행: {i + 1}/{len(texts)}")
                    
            except Exception as e:
                logger.error(f"BERT 분석 실패 (인덱스 {i}): {e}")
                results.append(self._fallback_analysis(text))
        
        return results
    
    def save_model(self, path: str):
        """모델 저장"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            model_data = {
                'model_name': self.model_name,
                'aspect_embeddings': self.aspect_embeddings,
                'aspect_keywords': self.aspect_keywords
            }
            
            with open(path, 'wb') as f:
                pickle.dump(model_data, f)
                
            logger.info(f"✅ BERT 모델 저장 완료: {path}")
            
        except Exception as e:
            logger.error(f"❌ BERT 모델 저장 실패: {e}")
    
    def load_model(self, path: str):
        """모델 로드"""
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            
            self.model_name = model_data['model_name']
            self.aspect_embeddings = model_data['aspect_embeddings']
            self.aspect_keywords = model_data['aspect_keywords']
            
            logger.info(f"✅ BERT 모델 로드 완료: {path}")
            
        except Exception as e:
            logger.error(f"❌ BERT 모델 로드 실패: {e}")


class BertSentimentManager:
    """BERT 감성 분석 매니저"""
    
    def __init__(self, model_name: str = "klue/bert-base"):
        self.analyzer = AspectBasedBertAnalyzer(model_name)
        self.cache = {}
    
    def analyze_review(self, text: str, use_cache: bool = True) -> BertSentimentResult:
        """리뷰 감성 분석"""
        if use_cache and text in self.cache:
            return self.cache[text]
        
        result = self.analyzer.analyze_sentiment(text)
        
        if use_cache:
            self.cache[text] = result
        
        return result
    
    def get_top_keywords(self, texts: List[str], aspect: str = None) -> List[Tuple[str, int]]:
        """상위 키워드 추출"""
        from collections import Counter
        
        all_keywords = []
        
        for text in texts:
            if aspect:
                # 특정 측면의 키워드만
                keywords = self.analyzer.aspect_keywords.get(aspect, [])
                for keyword in keywords:
                    if keyword in text:
                        all_keywords.append(keyword)
            else:
                # 모든 키워드
                for aspect_keywords in self.analyzer.aspect_keywords.values():
                    for keyword in aspect_keywords:
                        if keyword in text:
                            all_keywords.append(keyword)
        
        return Counter(all_keywords).most_common(10)


# 전역 BERT 분석기 인스턴스
try:
    bert_analyzer = BertSentimentManager()
    logger.info("✅ BERT 감성 분석기 초기화 완료")
except Exception as e:
    logger.error(f"❌ BERT 감성 분석기 초기화 실패: {e}")
    bert_analyzer = None


def analyze_with_bert(text: str) -> BertSentimentResult:
    """BERT 감성 분석 편의 함수"""
    if bert_analyzer:
        return bert_analyzer.analyze_review(text)
    else:
        # 폴백
        analyzer = AspectBasedBertAnalyzer()
        return analyzer._fallback_analysis(text)


def get_review_keywords(texts: List[str], top_n: int = 3) -> List[Tuple[str, int]]:
    """리뷰에서 상위 키워드 추출"""
    if bert_analyzer:
        return bert_analyzer.get_top_keywords(texts)[:top_n]
    else:
        return []