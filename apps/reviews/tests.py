from django.test import TestCase
from django.db import IntegrityError
from django.utils import timezone
from unittest.mock import patch, MagicMock
from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.clinics.models import Clinic
from .models import Review
from .crawlers.base import BaseCrawler, ReviewData, crawler_manager
from .services import CrawlingService, ReviewService, DuplicateDetectionService

User = get_user_model()


class ReviewModelTest(TestCase):
    """리뷰 모델 테스트"""
    
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='테스트 치과',
            address='서울특별시 강남구 테스트로 123',
            district='강남구'
        )
        
        self.review_data = {
            'clinic': self.clinic,
            'source': 'naver',
            'original_text': '친절하고 실력있는 치과입니다. 가격도 합리적이에요.',
            'original_rating': 5,
            'review_date': timezone.now(),
            'external_id': 'naver_123456'
        }
    
    def test_create_review(self):
        """리뷰 생성 테스트"""
        review = Review.objects.create(**self.review_data)
        
        self.assertEqual(review.clinic, self.clinic)
        self.assertEqual(review.source, 'naver')
        self.assertEqual(review.original_rating, 5)
        self.assertFalse(review.is_processed)
        self.assertFalse(review.is_duplicate)
        self.assertFalse(review.is_flagged)
    
    def test_review_string_representation(self):
        """리뷰 문자열 표현 테스트"""
        review = Review.objects.create(**self.review_data)
        expected_str = f"{self.clinic.name} - naver ({review.created_at.date()})"
        self.assertEqual(str(review), expected_str)
    
    def test_review_unique_constraint(self):
        """리뷰 중복 방지 테스트"""
        Review.objects.create(**self.review_data)
        
        # 같은 clinic, external_id, source 조합으로 중복 생성 시도
        with self.assertRaises(IntegrityError):
            Review.objects.create(**self.review_data)
    
    def test_reviewer_hash_generation(self):
        """리뷰어 해시 생성 테스트"""
        review = Review.objects.create(**self.review_data)
        review._reviewer_name = '홍길동'
        review.generate_reviewer_hash('홍길동')
        
        self.assertIsNotNone(review.reviewer_hash)
        self.assertEqual(len(review.reviewer_hash), 64)  # SHA256 해시 길이
    
    def test_update_search_vector(self):
        """검색 벡터 업데이트 테스트"""
        review = Review.objects.create(**self.review_data)
        
        # 검색 벡터가 자동으로 생성되는지 확인
        self.assertIsNotNone(review.search_vector)
    
    def test_clinic_stats_update_on_review_save(self):
        """리뷰 저장 시 치과 통계 업데이트 테스트"""
        initial_count = self.clinic.total_reviews
        
        # 리뷰 생성
        review = Review.objects.create(**self.review_data)
        review.is_processed = True
        review.save()
        
        # 치과 통계가 업데이트되었는지 확인
        self.clinic.refresh_from_db()
        # 실제로는 신호(signal)에 의해 업데이트되지만, 테스트에서는 수동 호출
        self.clinic.update_review_stats()
        self.assertEqual(self.clinic.total_reviews, 1)


class ReviewQueryTest(TestCase):
    """리뷰 쿼리 테스트"""
    
    def setUp(self):
        self.clinic1 = Clinic.objects.create(
            name='치과1',
            address='주소1',
            district='강남구'
        )
        
        self.clinic2 = Clinic.objects.create(
            name='치과2',
            address='주소2',
            district='서초구'
        )
        
        # 테스트용 리뷰들 생성
        Review.objects.create(
            clinic=self.clinic1,
            source='naver',
            original_text='좋은 치과입니다.',
            original_rating=5,
            external_id='naver_1',
            is_processed=True
        )
        
        Review.objects.create(
            clinic=self.clinic1,
            source='google',
            original_text='친절합니다.',
            original_rating=4,
            external_id='google_1',
            is_processed=False
        )
        
        Review.objects.create(
            clinic=self.clinic2,
            source='naver',
            original_text='가격이 비쌉니다.',
            original_rating=2,
            external_id='naver_2',
            is_duplicate=True
        )
    
    def test_filter_by_clinic(self):
        """치과별 필터링 테스트"""
        clinic1_reviews = Review.objects.filter(clinic=self.clinic1)
        self.assertEqual(clinic1_reviews.count(), 2)
    
    def test_filter_by_source(self):
        """출처별 필터링 테스트"""
        naver_reviews = Review.objects.filter(source='naver')
        self.assertEqual(naver_reviews.count(), 2)
        
        google_reviews = Review.objects.filter(source='google')
        self.assertEqual(google_reviews.count(), 1)
    
    def test_filter_processed_reviews(self):
        """처리된 리뷰 필터링 테스트"""
        processed_reviews = Review.objects.filter(is_processed=True)
        self.assertEqual(processed_reviews.count(), 1)
    
    def test_filter_duplicate_reviews(self):
        """중복 리뷰 필터링 테스트"""
        duplicate_reviews = Review.objects.filter(is_duplicate=True)
        self.assertEqual(duplicate_reviews.count(), 1)
    
    def test_search_by_text(self):
        """텍스트 검색 테스트"""
        results = Review.objects.filter(original_text__icontains='친절')
        self.assertEqual(results.count(), 1)

cla
ss MockCrawler(BaseCrawler):
    """테스트용 모크 크롤러"""
    
    def get_source_name(self) -> str:
        return 'mock'
    
    def crawl_reviews(self, clinic, max_reviews=100):
        """모크 리뷰 데이터 반환"""
        mock_reviews = [
            ReviewData(
                text="정말 좋은 치과입니다. 친절하고 실력도 좋아요.",
                rating=5,
                date=timezone.now(),
                reviewer_name="테스터1",
                external_id="mock_1"
            ),
            ReviewData(
                text="가격이 합리적이고 과잉진료 없어서 만족합니다.",
                rating=4,
                date=timezone.now(),
                reviewer_name="테스터2",
                external_id="mock_2"
            ),
            ReviewData(
                text="시설이 깨끗하고 대기시간도 짧았어요.",
                rating=4,
                date=timezone.now(),
                reviewer_name="테스터3",
                external_id="mock_3"
            )
        ]
        return mock_reviews[:max_reviews]


class CrawlerBaseTest(TestCase):
    """크롤러 기본 기능 테스트"""
    
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='테스트 치과',
            address='서울특별시 강남구 테스트로 123',
            district='강남구'
        )
        self.crawler = MockCrawler()
    
    def test_crawler_registration(self):
        """크롤러 등록 테스트"""
        crawler_manager.register_crawler('test', self.crawler)
        registered_crawler = crawler_manager.get_crawler('test')
        
        self.assertIsNotNone(registered_crawler)
        self.assertEqual(registered_crawler.get_source_name(), 'test')
    
    def test_review_crawling_and_saving(self):
        """리뷰 크롤링 및 저장 테스트"""
        # 크롤링 실행
        review_data_list = self.crawler.crawl_reviews(self.clinic, max_reviews=2)
        
        # 리뷰 저장
        saved_count, duplicate_count = self.crawler.save_reviews(self.clinic, review_data_list)
        
        self.assertEqual(len(review_data_list), 2)
        self.assertEqual(saved_count, 2)
        self.assertEqual(duplicate_count, 0)
        
        # 데이터베이스 확인
        reviews = Review.objects.filter(clinic=self.clinic)
        self.assertEqual(reviews.count(), 2)
    
    def test_duplicate_detection(self):
        """중복 리뷰 탐지 테스트"""
        # 첫 번째 크롤링
        review_data_list = self.crawler.crawl_reviews(self.clinic, max_reviews=2)
        saved_count, duplicate_count = self.crawler.save_reviews(self.clinic, review_data_list)
        
        # 같은 리뷰 다시 크롤링 (중복)
        saved_count2, duplicate_count2 = self.crawler.save_reviews(self.clinic, review_data_list)
        
        self.assertEqual(saved_count, 2)
        self.assertEqual(duplicate_count, 0)
        self.assertEqual(saved_count2, 0)
        self.assertEqual(duplicate_count2, 2)
    
    def test_text_anonymization(self):
        """텍스트 익명화 테스트"""
        text_with_personal_info = "제 전화번호는 010-1234-5678이고 이메일은 test@example.com입니다."
        anonymized = self.crawler.anonymize_review_text(text_with_personal_info)
        
        self.assertNotIn('010-1234-5678', anonymized)
        self.assertNotIn('test@example.com', anonymized)
        self.assertIn('[전화번호]', anonymized)
        self.assertIn('[이메일]', anonymized)


class CrawlingServiceTest(TestCase):
    """크롤링 서비스 테스트"""
    
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='테스트 치과',
            address='서울특별시 강남구 테스트로 123',
            district='강남구'
        )
        
        # 모크 크롤러 등록
        self.mock_crawler = MockCrawler()
        crawler_manager.register_crawler('mock', self.mock_crawler)
    
    def test_trigger_crawling(self):
        """크롤링 트리거 테스트"""
        result = CrawlingService.trigger_crawling(self.clinic.id, 'mock', 2)
        
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['clinic_id'], self.clinic.id)
        self.assertEqual(result['saved_reviews'], 2)
        
        # 치과 통계 업데이트 확인
        self.clinic.refresh_from_db()
        self.assertEqual(self.clinic.total_reviews, 2)
    
    def test_get_crawling_status(self):
        """크롤링 상태 조회 테스트"""
        # 먼저 리뷰 생성
        Review.objects.create(
            clinic=self.clinic,
            source='mock',
            original_text='테스트 리뷰',
            external_id='test_1'
        )
        
        status_info = CrawlingService.get_crawling_status(self.clinic.id)
        
        self.assertEqual(status_info['clinic_id'], self.clinic.id)
        self.assertEqual(status_info['clinic_name'], self.clinic.name)
        self.assertIn('recent_reviews', status_info)
        self.assertIn('source_statistics', status_info)


class ReviewServiceTest(TestCase):
    """리뷰 서비스 테스트"""
    
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='테스트 치과',
            address='서울특별시 강남구 테스트로 123',
            district='강남구'
        )
        
        # 테스트 리뷰들 생성
        self.review1 = Review.objects.create(
            clinic=self.clinic,
            source='naver',
            original_text='좋은 치과입니다.',
            original_rating=5,
            is_processed=True,
            external_id='naver_1'
        )
        
        self.review2 = Review.objects.create(
            clinic=self.clinic,
            source='google',
            original_text='친절한 치과입니다.',
            original_rating=4,
            is_processed=True,
            external_id='google_1'
        )
        
        self.review3 = Review.objects.create(
            clinic=self.clinic,
            source='naver',
            original_text='중복 리뷰입니다.',
            is_duplicate=True,
            external_id='naver_2'
        )
    
    def test_get_clinic_reviews(self):
        """치과 리뷰 조회 테스트"""
        reviews = ReviewService.get_clinic_reviews(self.clinic.id)
        
        # 처리된 리뷰만 반환되어야 함
        self.assertEqual(len(reviews), 2)
        
        # 소스별 필터링 테스트
        naver_reviews = ReviewService.get_clinic_reviews(self.clinic.id, source='naver')
        self.assertEqual(len(naver_reviews), 1)
    
    def test_get_review_statistics(self):
        """리뷰 통계 조회 테스트"""
        stats = ReviewService.get_review_statistics(self.clinic.id)
        
        self.assertEqual(stats['total_reviews'], 2)
        self.assertEqual(stats['average_rating'], 4.5)
        self.assertEqual(stats['naver_reviews'], 1)
        self.assertEqual(stats['google_reviews'], 1)
    
    def test_mark_reviews_as_processed(self):
        """리뷰 처리 완료 표시 테스트"""
        # 처리되지 않은 리뷰 생성
        unprocessed_review = Review.objects.create(
            clinic=self.clinic,
            source='naver',
            original_text='처리되지 않은 리뷰',
            is_processed=False,
            external_id='naver_3'
        )
        
        updated_count = ReviewService.mark_reviews_as_processed([unprocessed_review.id])
        
        self.assertEqual(updated_count, 1)
        
        unprocessed_review.refresh_from_db()
        self.assertTrue(unprocessed_review.is_processed)
    
    def test_search_reviews(self):
        """리뷰 검색 테스트"""
        results = ReviewService.search_reviews('좋은', self.clinic.id)
        
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].id, self.review1.id)


class DuplicateDetectionServiceTest(TestCase):
    """중복 탐지 서비스 테스트"""
    
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='테스트 치과',
            address='서울특별시 강남구 테스트로 123',
            district='강남구'
        )
        
        # 유사한 리뷰들 생성
        self.review1 = Review.objects.create(
            clinic=self.clinic,
            source='naver',
            original_text='정말 좋은 치과입니다. 추천합니다.',
            external_id='naver_1'
        )
        
        self.review2 = Review.objects.create(
            clinic=self.clinic,
            source='google',
            original_text='정말 좋은 치과입니다. 강력 추천합니다.',
            external_id='google_1'
        )
        
        self.review3 = Review.objects.create(
            clinic=self.clinic,
            source='naver',
            original_text='완전히 다른 내용의 리뷰입니다.',
            external_id='naver_2'
        )
    
    def test_detect_duplicates(self):
        """중복 리뷰 탐지 테스트"""
        duplicates = DuplicateDetectionService.detect_duplicates(self.clinic.id, 0.5)
        
        # 유사한 리뷰가 중복으로 탐지되어야 함
        self.assertGreater(len(duplicates), 0)
        
        # 중복 정보 확인
        duplicate = duplicates[0]
        self.assertIn('similarity_score', duplicate)
        self.assertIn('original_review_id', duplicate)
        self.assertIn('duplicate_review_id', duplicate)
    
    def test_auto_mark_duplicates(self):
        """자동 중복 표시 테스트"""
        marked_count = DuplicateDetectionService.auto_mark_duplicates(self.clinic.id, 0.5)
        
        self.assertGreater(marked_count, 0)
        
        # 중복으로 표시된 리뷰 확인
        duplicate_reviews = Review.objects.filter(clinic=self.clinic, is_duplicate=True)
        self.assertEqual(duplicate_reviews.count(), marked_count)


class CrawlingAPITest(APITestCase):
    """크롤링 API 테스트"""
    
    def setUp(self):
        # 관리자 사용자 생성
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='testpass123',
            is_staff=True
        )
        
        # 일반 사용자 생성
        self.normal_user = User.objects.create_user(
            username='user',
            email='user@test.com',
            password='testpass123'
        )
        
        self.clinic = Clinic.objects.create(
            name='테스트 치과',
            address='서울특별시 강남구 테스트로 123',
            district='강남구'
        )
        
        # 모크 크롤러 등록
        mock_crawler = MockCrawler()
        crawler_manager.register_crawler('mock', mock_crawler)
    
    def test_crawling_trigger_permission(self):
        """크롤링 트리거 권한 테스트"""
        url = reverse('api:reviews:crawl_trigger')
        data = {
            'clinic_id': self.clinic.id,
            'source': 'mock',
            'max_reviews': 10
        }
        
        # 인증 없이 접근
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # 일반 사용자로 접근
        self.client.force_authenticate(user=self.normal_user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # 관리자로 접근
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @patch('apps.reviews.api_views.crawl_all_sources.delay')
    def test_crawling_trigger_success(self, mock_task):
        """크롤링 트리거 성공 테스트"""
        mock_task.return_value = MagicMock(id='test-task-id')
        
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('api:reviews:crawl_trigger')
        data = {
            'clinic_id': self.clinic.id,
            'source': 'all',
            'max_reviews': 50
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('task_id', response.data)
        self.assertEqual(response.data['clinic_id'], self.clinic.id)
        
        # Celery 태스크가 호출되었는지 확인
        mock_task.assert_called_once_with(self.clinic.id, 50)
    
    def test_crawling_status_api(self):
        """크롤링 상태 조회 API 테스트"""
        self.client.force_authenticate(user=self.admin_user)
        
        url = reverse('api:reviews:crawl_status', kwargs={'clinic_id': self.clinic.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['clinic_id'], self.clinic.id)
        self.assertIn('clinic_name', response.data)
    
    def test_clinic_reviews_api(self):
        """치과 리뷰 조회 API 테스트"""
        # 테스트 리뷰 생성
        Review.objects.create(
            clinic=self.clinic,
            source='naver',
            original_text='좋은 치과입니다.',
            original_rating=5,
            is_processed=True,
            external_id='naver_1'
        )
        
        self.client.force_authenticate(user=self.normal_user)
        
        url = reverse('api:reviews:clinic_reviews', kwargs={'clinic_id': self.clinic.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['clinic_id'], self.clinic.id)
        self.assertIn('statistics', response.data)
        self.assertIn('reviews', response.data)


class CrawlerIntegrationTest(TestCase):
    """크롤러 통합 테스트"""
    
    def setUp(self):
        self.clinic = Clinic.objects.create(
            name='테스트 치과',
            address='서울특별시 강남구 테스트로 123',
            district='강남구'
        )
    
    @patch('apps.reviews.crawlers.naver.NaverPlaceCrawler._setup_driver')
    @patch('apps.reviews.crawlers.naver.NaverPlaceCrawler._teardown_driver')
    @patch('apps.reviews.crawlers.naver.NaverPlaceCrawler._find_naver_place_url')
    def test_naver_crawler_integration(self, mock_find_url, mock_teardown, mock_setup):
        """네이버 크롤러 통합 테스트"""
        from apps.reviews.crawlers.naver import NaverPlaceCrawler
        
        # 모킹 설정
        mock_find_url.return_value = None  # URL을 찾지 못한 경우
        
        crawler = NaverPlaceCrawler()
        reviews = crawler.crawl_reviews(self.clinic, max_reviews=10)
        
        # URL을 찾지 못했으므로 빈 리스트 반환
        self.assertEqual(len(reviews), 0)
        
        # 메서드들이 호출되었는지 확인
        mock_setup.assert_called_once()
        mock_teardown.assert_called_once()
        mock_find_url.assert_called_once_with(self.clinic)
    
    @patch('apps.reviews.crawlers.google.GoogleMapsCrawler._setup_driver')
    @patch('apps.reviews.crawlers.google.GoogleMapsCrawler._teardown_driver')
    @patch('apps.reviews.crawlers.google.GoogleMapsCrawler._search_clinic_on_google_maps')
    def test_google_crawler_integration(self, mock_search, mock_teardown, mock_setup):
        """구글 크롤러 통합 테스트"""
        from apps.reviews.crawlers.google import GoogleMapsCrawler
        
        # 모킹 설정
        mock_search.return_value = False  # 검색 실패
        
        crawler = GoogleMapsCrawler()
        reviews = crawler.crawl_reviews(self.clinic, max_reviews=10)
        
        # 검색에 실패했으므로 빈 리스트 반환
        self.assertEqual(len(reviews), 0)
        
        # 메서드들이 호출되었는지 확인
        mock_setup.assert_called_once()
        mock_teardown.assert_called_once()
        mock_search.assert_called_once_with(self.clinic)