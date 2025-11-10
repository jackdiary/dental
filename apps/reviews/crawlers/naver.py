"""
네이버 플레이스 리뷰 크롤러
"""
from typing import List, Optional
from datetime import datetime
import re
import time
import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from apps.clinics.models import Clinic
from .base import BaseCrawler, ReviewData

logger = logging.getLogger(__name__)


class NaverPlaceCrawler(BaseCrawler):
    """네이버 플레이스 크롤러"""
    
    def __init__(self, delay_seconds: int = 3, headless: bool = True):
        super().__init__(delay_seconds)
        self.headless = headless
        self.driver = None
    
    def get_source_name(self) -> str:
        return 'naver'
    
    def _setup_driver(self):
        """Selenium WebDriver 설정"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        try:
            # ChromeDriverManager를 사용하여 자동으로 드라이버 다운로드 및 설정
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # 자동화 감지 방지
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            self.driver.implicitly_wait(10)
            logger.info("Chrome WebDriver 초기화 완료")
        except Exception as e:
            logger.error(f"WebDriver 초기화 실패: {e}")
            raise
    
    def _teardown_driver(self):
        """WebDriver 정리"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def crawl_reviews(self, clinic: Clinic, max_reviews: int = 100) -> List[ReviewData]:
        """네이버 플레이스 리뷰 크롤링"""
        reviews = []
        
        try:
            self._setup_driver()
            
            # 네이버 플레이스 URL 생성 또는 검색
            place_url = self._find_naver_place_url(clinic)
            if not place_url:
                logger.warning(f"네이버 플레이스를 찾을 수 없습니다: {clinic.name}")
                return reviews
            
            # 리뷰 페이지로 이동
            review_url = self._get_review_page_url(place_url)
            self.driver.get(review_url)
            
            # 리뷰 로딩 대기
            self._wait_for_reviews_to_load()
            
            # 리뷰 수집
            reviews = self._extract_reviews(max_reviews)
            
            logger.info(f"네이버 플레이스 리뷰 수집 완료: {clinic.name} - {len(reviews)}개")
            
        except Exception as e:
            logger.error(f"네이버 플레이스 크롤링 실패: {clinic.name} - {e}")
            self.error_count += 1
        
        finally:
            self._teardown_driver()
        
        return reviews
    
    def _find_naver_place_url(self, clinic: Clinic) -> Optional[str]:
        """네이버 플레이스 URL 찾기"""
        # 이미 naver_place_id가 있는 경우
        if clinic.naver_place_id:
            return f"https://place.naver.com/place/{clinic.naver_place_id}"
        
        # 검색을 통해 찾기
        search_query = f"{clinic.name} {clinic.district}"
        search_url = f"https://map.naver.com/v5/search/{search_query}"
        
        try:
            self.driver.get(search_url)
            self.add_delay()
            
            # 검색 결과에서 첫 번째 결과 클릭
            first_result = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "._3ZUQs"))
            )
            first_result.click()
            
            self.add_delay()
            
            # 현재 URL에서 place ID 추출
            current_url = self.driver.current_url
            place_id_match = re.search(r'/place/(\d+)', current_url)
            
            if place_id_match:
                place_id = place_id_match.group(1)
                # 치과 정보 업데이트
                clinic.naver_place_id = place_id
                clinic.save(update_fields=['naver_place_id'])
                
                return f"https://place.naver.com/place/{place_id}"
        
        except Exception as e:
            logger.error(f"네이버 플레이스 검색 실패: {clinic.name} - {e}")
        
        return None
    
    def _get_review_page_url(self, place_url: str) -> str:
        """리뷰 페이지 URL 생성"""
        return f"{place_url}/review/visitor"
    
    def _wait_for_reviews_to_load(self):
        """리뷰 로딩 대기"""
        try:
            WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, ".YeINN"))
            )
        except TimeoutException:
            logger.warning("리뷰 로딩 시간 초과")
    
    def _extract_reviews(self, max_reviews: int) -> List[ReviewData]:
        """리뷰 데이터 추출"""
        reviews = []
        collected_count = 0
        
        while collected_count < max_reviews:
            try:
                # 현재 페이지의 리뷰들 추출
                page_reviews = self._extract_reviews_from_current_page()
                
                if not page_reviews:
                    logger.info("더 이상 리뷰가 없습니다.")
                    break
                
                reviews.extend(page_reviews)
                collected_count += len(page_reviews)
                
                # 다음 페이지로 이동
                if not self._go_to_next_page():
                    logger.info("마지막 페이지에 도달했습니다.")
                    break
                
                self.add_delay()
                
            except Exception as e:
                logger.error(f"리뷰 추출 중 오류: {e}")
                break
        
        return reviews[:max_reviews]
    
    def _extract_reviews_from_current_page(self) -> List[ReviewData]:
        """현재 페이지에서 리뷰 추출"""
        reviews = []
        
        try:
            # 페이지 소스 가져오기
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # 리뷰 요소들 찾기
            review_elements = soup.find_all('div', class_='YeINN')
            
            for element in review_elements:
                try:
                    review_data = self._parse_review_element(element)
                    if review_data:
                        reviews.append(review_data)
                except Exception as e:
                    logger.error(f"개별 리뷰 파싱 실패: {e}")
                    continue
        
        except Exception as e:
            logger.error(f"페이지 리뷰 추출 실패: {e}")
        
        return reviews
    
    def _parse_review_element(self, element) -> Optional[ReviewData]:
        """개별 리뷰 요소 파싱"""
        try:
            # 리뷰 텍스트
            text_elem = element.find('span', class_='zPfVt')
            if not text_elem:
                return None
            
            text = text_elem.get_text(strip=True)
            if not text or len(text) < 10:  # 너무 짧은 리뷰 제외
                return None
            
            # 평점
            rating = None
            rating_elem = element.find('div', class_='PXMot')
            if rating_elem:
                rating_text = rating_elem.get('aria-label', '')
                rating_match = re.search(r'(\d+)점', rating_text)
                if rating_match:
                    rating = int(rating_match.group(1))
            
            # 작성일
            date = None
            date_elem = element.find('time')
            if date_elem:
                date_str = date_elem.get('datetime')
                if date_str:
                    try:
                        date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except ValueError:
                        pass
            
            # 리뷰어 이름 (익명화를 위해 수집하지만 저장하지 않음)
            reviewer_name = None
            reviewer_elem = element.find('div', class_='dAsGb')
            if reviewer_elem:
                reviewer_name = reviewer_elem.get_text(strip=True)
            
            # 외부 ID (리뷰 고유 식별자)
            external_id = None
            review_id_elem = element.get('data-review-id')
            if review_id_elem:
                external_id = f"naver_{review_id_elem}"
            
            return ReviewData(
                text=text,
                rating=rating,
                date=date,
                reviewer_name=reviewer_name,
                external_id=external_id
            )
        
        except Exception as e:
            logger.error(f"리뷰 요소 파싱 실패: {e}")
            return None
    
    def _go_to_next_page(self) -> bool:
        """다음 페이지로 이동"""
        try:
            # 다음 페이지 버튼 찾기
            next_button = self.driver.find_element(By.CSS_SELECTOR, ".fvwqf")
            
            if next_button.is_enabled():
                next_button.click()
                self.add_delay()
                return True
            else:
                return False
        
        except NoSuchElementException:
            return False
        except Exception as e:
            logger.error(f"다음 페이지 이동 실패: {e}")
            return False
    
    def _scroll_to_load_more_reviews(self):
        """스크롤하여 더 많은 리뷰 로드"""
        try:
            # 페이지 끝까지 스크롤
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            self.add_delay()
            
            # "더보기" 버튼이 있으면 클릭
            try:
                more_button = self.driver.find_element(By.CSS_SELECTOR, ".fvwqf")
                if more_button.is_displayed() and more_button.is_enabled():
                    more_button.click()
                    self.add_delay()
            except NoSuchElementException:
                pass
        
        except Exception as e:
            logger.error(f"스크롤 로딩 실패: {e}")


# 크롤러 인스턴스 생성 및 등록
def register_naver_crawler():
    """네이버 크롤러 등록"""
    from .base import crawler_manager
    
    naver_crawler = NaverPlaceCrawler()
    crawler_manager.register_crawler('naver', naver_crawler)
    logger.info("네이버 플레이스 크롤러 등록 완료")


# 모듈 로드 시 자동 등록
register_naver_crawler()