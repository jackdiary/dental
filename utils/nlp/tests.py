"""
NLP 유틸리티 테스트
"""
import unittest
from django.test import TestCase
from .korean_analyzer import (
    korean_analyzer, 
    analyze_korean_text, 
    extract_dental_aspects,
    preprocess_for_ml,
    OktAnalyzer,
    Token,
    AnalysisResult
)
from .preprocessing import (
    ReviewPreprocessor,
    ReviewPreprocessingPipeline,
    PreprocessingConfig,
    TextQualityAnalyzer,
    preprocess_review_text,
    batch_preprocess_reviews
)


class KoreanAnalyzerTest(TestCase):
    """한국어 분석기 테스트"""
    
    def setUp(self):
        self.sample_texts = [
            "정말 좋은 치과입니다. 의사선생님이 친절하시고 실력도 뛰어나세요.",
            "스케일링 받았는데 가격이 합리적이었어요. 과잉진료도 없고 만족합니다.",
            "시설이 깨끗하고 현대적이에요. 대기시간도 짧아서 좋았습니다.",
            "임플란트 상담받았는데 자세히 설명해주셔서 신뢰가 갔어요.",
            "아픈데 친절하게 치료해주셔서 감사했습니다. 추천해요!"
        ]
    
    def test_korean_text_analysis(self):
        """한국어 텍스트 분석 테스트"""
        text = self.sample_texts[0]
        result = analyze_korean_text(text)
        
        self.assertIsInstance(result, AnalysisResult)
        self.assertEqual(result.original_text, text)
        self.assertGreater(len(result.tokens), 0)
        self.assertGreater(len(result.nouns), 0)
        self.assertIsInstance(result.cleaned_text, str)
    
    def test_dental_aspects_extraction(self):
        """치과 관련 측면 추출 테스트"""
        text = "스케일링 받았는데 가격이 합리적이고 의사선생님이 친절하세요."
        aspects = extract_dental_aspects(text)
        
        self.assertIsInstance(aspects, dict)
        self.assertIn('treatment', aspects)
        self.assertIn('price', aspects)
        self.assertIn('quality', aspects)
        
        # 치료 관련 키워드 확인
        treatment_keywords = aspects.get('treatment', [])
        self.assertTrue(any('스케일링' in keyword for keyword in treatment_keywords))
    
    def test_ml_preprocessing(self):
        """ML용 전처리 테스트"""
        text = "정말 좋은 치과입니다! 의사선생님이 너무 친절하세요 ㅎㅎ"
        processed = preprocess_for_ml(text)
        
        self.assertIsInstance(processed, str)
        self.assertNotIn('ㅎㅎ', processed)  # 의미없는 문자 제거
        self.assertNotIn('너무', processed)  # 불용어 제거
    
    def test_analyzer_manager(self):
        """분석기 매니저 테스트"""
        text = self.sample_texts[1]
        
        # 기본 분석기 테스트
        result1 = korean_analyzer.analyze_text(text)
        self.assertIsInstance(result1, AnalysisResult)
        
        # 특정 분석기 지정 테스트
        result2 = korean_analyzer.analyze_text(text, 'okt')
        self.assertIsInstance(result2, AnalysisResult)
    
    def test_batch_analysis(self):
        """일괄 분석 테스트"""
        results = korean_analyzer.batch_analyze(self.sample_texts[:3])
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result, AnalysisResult)
    
    def test_keyword_extraction(self):
        """키워드 추출 테스트"""
        analyzer = OktAnalyzer()
        text = "임플란트 치료를 받았는데 정말 만족스러웠습니다."
        result = analyzer.analyze(text)
        
        keywords = analyzer.extract_keywords(result.tokens)
        self.assertIsInstance(keywords, list)
        self.assertTrue(any('임플란트' in keyword for keyword in keywords))
    
    def test_stopwords_filtering(self):
        """불용어 필터링 테스트"""
        analyzer = OktAnalyzer()
        
        # 불용어가 포함된 텍스트
        text = "이것은 정말 좋은 치과입니다."
        result = analyzer.analyze(text)
        keywords = analyzer.extract_keywords(result.tokens)
        
        # 불용어가 키워드에서 제외되었는지 확인
        self.assertNotIn('이것', keywords)
        self.assertNotIn('정말', keywords)


class PreprocessingTest(TestCase):
    """전처리 테스트"""
    
    def setUp(self):
        self.config = PreprocessingConfig(
            remove_special_chars=True,
            normalize_whitespace=True,
            remove_short_words=True,
            min_word_length=2,
            remove_stopwords=True,
            extract_keywords=True,
            max_keywords=10
        )
        self.preprocessor = ReviewPreprocessor(self.config)
        
        self.sample_reviews = [
            "정말 좋은 치과예요!!! 의사선생님이 친절하시고 실력도 좋아요 ^^",
            "스케일링 받았는데... 가격이 10만원이었어요. 합리적인 것 같아요.",
            "시설이 깨끗하고 대기시간도 짧았습니다. 추천합니다!",
            "과잉진료 없이 정직하게 치료해주셔서 감사했어요.",
            "전화번호: 010-1234-5678, 이메일: test@example.com"  # 개인정보 포함
        ]
    
    def test_single_review_preprocessing(self):
        """단일 리뷰 전처리 테스트"""
        text = self.sample_reviews[0]
        result = self.preprocessor.preprocess_single(text)
        
        self.assertEqual(result.original_text, text)
        self.assertIsInstance(result.cleaned_text, str)
        self.assertIsInstance(result.processed_text, str)
        self.assertIsInstance(result.keywords, list)
        self.assertIsInstance(result.dental_aspects, dict)
        self.assertIsInstance(result.metadata, dict)
        
        # 특수문자 제거 확인
        self.assertNotIn('!!!', result.cleaned_text)
        self.assertNotIn('^^', result.cleaned_text)
    
    def test_text_cleaning(self):
        """텍스트 정제 테스트"""
        dirty_text = "정말   좋은    치과예요!!! @#$%^&*()"
        cleaned = self.preprocessor._clean_text(dirty_text)
        
        # 연속 공백 정리 확인
        self.assertNotIn('   ', cleaned)
        # 특수문자 제거 확인
        self.assertNotIn('@#$%', cleaned)
    
    def test_personal_info_removal(self):
        """개인정보 제거 테스트"""
        text_with_personal_info = self.sample_reviews[4]
        result = self.preprocessor.preprocess_single(text_with_personal_info)
        
        # 전화번호와 이메일이 제거되었는지 확인
        self.assertNotIn('010-1234-5678', result.cleaned_text)
        self.assertNotIn('test@example.com', result.cleaned_text)
        self.assertIn('[전화번호]', result.cleaned_text)
        self.assertIn('[이메일]', result.cleaned_text)
    
    def test_keyword_extraction(self):
        """키워드 추출 테스트"""
        text = "스케일링 치료를 받았는데 가격이 합리적이고 의사가 친절했어요."
        result = self.preprocessor.preprocess_single(text)
        
        self.assertIsInstance(result.keywords, list)
        self.assertGreater(len(result.keywords), 0)
        
        # 치과 관련 키워드가 포함되었는지 확인
        keywords_text = ' '.join(result.keywords)
        self.assertTrue(any(keyword in keywords_text for keyword in ['스케일링', '치료', '가격', '친절']))
    
    def test_dental_aspects_categorization(self):
        """치과 측면 분류 테스트"""
        text = "임플란트 수술 받았는데 가격이 비싸지만 의사선생님이 친절하세요."
        result = self.preprocessor.preprocess_single(text)
        
        aspects = result.dental_aspects
        self.assertIsInstance(aspects, dict)
        
        # 각 카테고리가 존재하는지 확인
        expected_categories = ['treatment', 'price', 'quality', 'facility', 'service', 'overtreatment']
        for category in expected_categories:
            self.assertIn(category, aspects)
    
    def test_batch_preprocessing(self):
        """일괄 전처리 테스트"""
        results = self.preprocessor.preprocess_batch(self.sample_reviews[:3])
        
        self.assertEqual(len(results), 3)
        for result in results:
            self.assertIsInstance(result.original_text, str)
            self.assertIsInstance(result.processed_text, str)
    
    def test_preprocessing_pipeline(self):
        """전처리 파이프라인 테스트"""
        pipeline = ReviewPreprocessingPipeline(self.config)
        results = pipeline.process_reviews(self.sample_reviews[:3])
        
        self.assertEqual(len(results), 3)
        
        # 통계 확인
        self.assertGreater(pipeline.stats['total_processed'], 0)
        self.assertGreaterEqual(pipeline.stats['successful'], 0)
    
    def test_fallback_processing(self):
        """폴백 처리 테스트"""
        # 빈 텍스트나 문제가 있는 텍스트
        problematic_texts = ["", "   ", "!@#$%^&*()"]
        
        for text in problematic_texts:
            result = self.preprocessor.preprocess_single(text)
            self.assertIsInstance(result.original_text, str)
            self.assertIsInstance(result.cleaned_text, str)


class TextQualityAnalyzerTest(TestCase):
    """텍스트 품질 분석기 테스트"""
    
    def test_quality_analysis(self):
        """품질 분석 테스트"""
        # 고품질 텍스트
        high_quality_text = "정말 좋은 치과입니다. 의사선생님이 친절하시고 실력도 뛰어나세요. 스케일링을 받았는데 가격도 합리적이었어요."
        
        scores = TextQualityAnalyzer.analyze_quality(high_quality_text)
        
        self.assertIsInstance(scores, dict)
        self.assertIn('overall_score', scores)
        self.assertIn('length_score', scores)
        self.assertIn('korean_ratio_score', scores)
        
        # 점수가 0-1 범위인지 확인
        for score_name, score_value in scores.items():
            self.assertGreaterEqual(score_value, 0.0)
            self.assertLessEqual(score_value, 1.0)
    
    def test_low_quality_detection(self):
        """저품질 텍스트 탐지 테스트"""
        # 저품질 텍스트들
        low_quality_texts = [
            "ㅋㅋㅋㅋㅋㅋㅋㅋㅋㅋ",  # 의미없는 반복
            "a",  # 너무 짧음
            "!@#$%^&*()!@#$%^&*()",  # 특수문자만
            "abcdefghijklmnopqrstuvwxyz" * 50  # 너무 긺
        ]
        
        for text in low_quality_texts:
            is_high_quality = TextQualityAnalyzer.is_high_quality(text)
            self.assertFalse(is_high_quality, f"텍스트가 고품질로 잘못 판단됨: {text[:20]}...")
    
    def test_high_quality_detection(self):
        """고품질 텍스트 탐지 테스트"""
        high_quality_texts = [
            "정말 좋은 치과입니다. 의사선생님이 친절하시고 치료도 꼼꼼하게 해주세요.",
            "스케일링 받았는데 가격이 합리적이고 과잉진료 없이 정직하게 치료해주셨어요.",
            "시설이 깨끗하고 최신 장비를 사용하셔서 안심이 되었습니다."
        ]
        
        for text in high_quality_texts:
            is_high_quality = TextQualityAnalyzer.is_high_quality(text)
            self.assertTrue(is_high_quality, f"텍스트가 저품질로 잘못 판단됨: {text[:20]}...")
    
    def test_korean_ratio_scoring(self):
        """한글 비율 점수 테스트"""
        # 한글 비율이 높은 텍스트
        korean_text = "정말 좋은 치과입니다."
        scores = TextQualityAnalyzer.analyze_quality(korean_text)
        self.assertGreater(scores['korean_ratio_score'], 0.8)
        
        # 한글 비율이 낮은 텍스트
        english_text = "This is English text with some 한글."
        scores = TextQualityAnalyzer.analyze_quality(english_text)
        self.assertLess(scores['korean_ratio_score'], 0.8)
    
    def test_length_scoring(self):
        """길이 점수 테스트"""
        # 적정 길이 텍스트 (50-500자)
        optimal_text = "정말 좋은 치과입니다. " * 5  # 약 100자
        scores = TextQualityAnalyzer.analyze_quality(optimal_text)
        self.assertGreater(scores['length_score'], 0.8)
        
        # 너무 짧은 텍스트
        short_text = "좋아요"
        scores = TextQualityAnalyzer.analyze_quality(short_text)
        self.assertLess(scores['length_score'], 0.5)


class PreprocessingIntegrationTest(TestCase):
    """전처리 통합 테스트"""
    
    def test_end_to_end_preprocessing(self):
        """전체 전처리 플로우 테스트"""
        # 실제 리뷰와 유사한 텍스트
        review_text = """
        정말 좋은 치과입니다!!! 
        의사선생님이 너무 친절하시고 실력도 뛰어나세요 ^^
        스케일링 받았는데 가격이 8만원이었어요. 
        다른 곳보다 저렴하고 과잉진료도 없어서 만족합니다.
        시설도 깨끗하고 대기시간도 짧았어요~
        적극 추천합니다! 연락처: 010-1234-5678
        """
        
        # 전처리 실행
        result = preprocess_review_text(review_text)
        
        # 결과 검증
        self.assertIsInstance(result.original_text, str)
        self.assertIsInstance(result.cleaned_text, str)
        self.assertIsInstance(result.processed_text, str)
        self.assertIsInstance(result.keywords, list)
        
        # 개인정보 제거 확인
        self.assertNotIn('010-1234-5678', result.cleaned_text)
        
        # 특수문자 정리 확인
        self.assertNotIn('!!!', result.cleaned_text)
        self.assertNotIn('^^', result.cleaned_text)
        
        # 키워드 추출 확인
        self.assertGreater(len(result.keywords), 0)
        
        # 치과 관련 측면 분류 확인
        self.assertIn('treatment', result.dental_aspects)
        self.assertIn('price', result.dental_aspects)
    
    def test_batch_processing_performance(self):
        """일괄 처리 성능 테스트"""
        # 여러 리뷰 텍스트 생성
        review_texts = [
            f"치과 리뷰 {i}번입니다. 정말 좋은 치과예요. 의사선생님이 친절하시고 실력도 좋아요."
            for i in range(10)
        ]
        
        # 일괄 처리
        results = batch_preprocess_reviews(review_texts)
        
        # 결과 검증
        self.assertEqual(len(results), len(review_texts))
        
        for i, result in enumerate(results):
            self.assertIn(f"치과 리뷰 {i}번", result.original_text)
            self.assertIsInstance(result.processed_text, str)
    
    def test_error_handling(self):
        """오류 처리 테스트"""
        # 문제가 있는 텍스트들
        problematic_texts = [
            None,  # None 값
            "",    # 빈 문자열
            "   ", # 공백만
            "a" * 10000,  # 너무 긴 텍스트
        ]
        
        for text in problematic_texts:
            if text is None:
                continue
                
            try:
                result = preprocess_review_text(text)
                # 오류가 발생하지 않고 결과가 반환되어야 함
                self.assertIsInstance(result.original_text, str)
            except Exception as e:
                self.fail(f"전처리 중 예상치 못한 오류 발생: {e}")


if __name__ == '__main__':
    unittest.main()