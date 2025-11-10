"""
구글 맵 리뷰 크롤러
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
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from apps.clinics.models import Clinic
from .base import BaseCrawler, ReviewData

logger = logging.getLogger(__name__)


class GoogleMapsCrawler(BaseCrawler):
    """구글 맵 크롤러"""
    
    def __init__(self, delay_seconds: int = 3, headless: bool = True):
        super().__init__(delay_seconds)
        self.headless = headless
        self.driver = None
    
    def get_source_name(self) -> str:
        return 'google'
    
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
        chrome_options.add_argument('--lang=ko-KR')
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
            logger.info("Chrome WebDriver 초기화 완료 (Google Maps)")
        except Exception as e:
            logger.error(f"WebDriver 초기화 실패: {e}")
            raise
    
    def _teardown_driver(self):
        """WebDriver 정리"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def crawl_reviews(self, clinic: Clinic, max_reviews: int = 100) -> List[ReviewData]:
        """구글 맵 리뷰 크롤링"""
        reviews = []
        
        try:
            self._setup_driver()
            
            # 구글 맵에서 치과 검색
            if not self._search_clinic_on_google_maps(clinic):
                logger.warning(f"구글 맵에서 치과를 찾을 수 없습니다: {clinic.name}")
                return reviews
            
            # 리뷰 섹션으로 이동
            if not self._navigate_to_reviews_section():
                logger.warning(f"리뷰 섹션을 찾을 수 없습니다: {clinic.name}")
                return reviews
            
            # 리뷰 수집
            reviews = self._extract_reviews(max_reviews)
            
            logger.info(f"구글 맵 리뷰 수집 완료: {clinic.name} - {len(reviews)}개")
            
        except Exception as e:
            logger.error(f"구글 맵 크롤링 실패: {clinic.name} - {e}")
            self.error_count += 1
        
        finally:
            self._teardown_driver()
        
        return reviews
    
    def _search_clinic_on_google_maps(self, clinic: Clinic) -> bool:
        """구글 맵에서 치과 검색"""
        try:
            # 구글 맵 접속
            self.driver.get("https://maps.google.com")
            self.add_delay()
            
            # 검색어 입력
            search_query = f"{clinic.name} {clinic.address}"
            search_box = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "searchboxinput"))
            )
            
            search_box.clear()
            search_box.send_keys(search_query)
            search_box.send_keys(Keys.ENTER)
            
            self.add_delay()
            
            # 검색 결과 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-value='Reviews']"))
            )
            
            # Place ID 추출 및 저장
            self._extract_and_save_place_id(clinic)
            
            return True
            
        except Exception as e:
            logger.error(f"구글 맵 검색 실패: {clinic.name} - {e}")
            return False
    
    def _extract_and_save_place_id(self, clinic: Clinic):
        """Place ID 추출 및 저장"""
        try:
            current_url = self.driver.current_url
            place_id_match = re.search(r'place/([^/]+)', current_url)
            
            if place_id_match and not clinic.google_place_id:
                place_id = place_id_match.group(1)
                clinic.google_place_id = place_id
                clinic.save(update_fields=['google_place_id'])
                logger.info(f"Google Place ID 저장: {clinic.name} - {place_id}")
        
        except Exception as e:
            logger.error(f"Place ID 추출 실패: {e}")
    
    def _navigate_to_reviews_section(self) -> bool:
        """리뷰 섹션으로 이동"""
        try:
            # 리뷰 탭 클릭
            reviews_tab = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-value='Reviews']"))
            )
            reviews_tab.click()
            
            self.add_delay()
            
            # 리뷰 목록 로딩 대기
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-review-id]"))
            )
            
            return True
            
        except Exception as e:
            logger.error(f"리뷰 섹션 이동 실패: {e}")
            return False
    
    def _extract_reviews(self, max_reviews: int) -> List[ReviewData]:
        """리뷰 데이터 추출"""
        reviews = []
        collected_count = 0
        scroll_attempts = 0
        max_scroll_attempts = 20
        
        while collected_count < max_reviews and scroll_attempts < max_scroll_attempts:
            try:
                # 현재 페이지의 리뷰들 추출
                page_reviews = self._extract_reviews_from_current_page()
                
                # 새로운 리뷰만 추가
                new_reviews = []
                for review in page_reviews:
                    if review.external_id not in [r.external_id for r in reviews]:
                        new_reviews.append(review)
                
                if not new_reviews:
                    # 더 많은 리뷰를 로드하기 위해 스크롤
                    if not self._scroll_to_load_more_reviews():
                        logger.info("더 이상 리뷰가 없습니다.")
                        break
                    scroll_attempts += 1
                    continue
                
                reviews.extend(new_reviews)
                collected_count += len(new_reviews)
                
                logger.info(f"수집된 리뷰: {collected_count}/{max_reviews}")
                
                # 더 많은 리뷰 로드
                self._scroll_to_load_more_reviews()
                scroll_attempts += 1
                
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
            review_elements = soup.find_all('div', {'data-review-id': True})
            
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
            # 외부 ID
            external_id = element.get('data-review-id')
            if not external_id:
                return None
            
            external_id = f"google_{external_id}"
            
            # 리뷰 텍스트
            text_elem = element.find('span', {'data-expandable-section': True})
            if not text_elem:
                # 대체 선택자 시도
                text_elem = element.find('div', class_='MyEned')
            
            if not text_elem:
                return None
            
            text = text_elem.get_text(strip=True)
            if not text or len(text) < 10:  # 너무 짧은 리뷰 제외
                return None
            
            # 평점
            rating = None
            rating_elem = element.find('span', class_='kvMYJc')
            if rating_elem:
                rating_attr = rating_elem.get('aria-label', '')
                rating_match = re.search(r'(\d+)점', rating_attr)
                if rating_match:
                    rating = int(rating_match.group(1))
                else:
                    # 별점 개수로 계산
                    stars = len(rating_elem.find_all('span', class_='hCCjke'))
                    if stars > 0:
                        rating = stars
            
            # 작성일
            date = None
            date_elem = element.find('span', class_='rsqaWe')
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                date = self._parse_relative_date(date_text)
            
            # 리뷰어 이름
            reviewer_name = None
            reviewer_elem = element.find('div', class_='d4r55')
            if reviewer_elem:
                reviewer_name = reviewer_elem.get_text(strip=True)
            
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
    
    def _parse_relative_date(self, date_text: str) -> Optional[datetime]:
        """상대적 날짜 텍스트를 datetime으로 변환"""
        try:
            from datetime import timedelta
            from django.utils import timezone
            
            now = timezone.now()
            
            # 한국어 패턴 매칭
            if '일 전' in date_text:
                days_match = re.search(r'(\d+)일 전', date_text)
                if days_match:
                    days = int(days_match.group(1))
                    return now - timedelta(days=days)
            
            elif '주 전' in date_text or '주일 전' in date_text:
                weeks_match = re.search(r'(\d+)주', date_text)
                if weeks_match:
                    weeks = int(weeks_match.group(1))
                    return now - timedelta(weeks=weeks)
            
            elif '개월 전' in date_text:
                months_match = re.search(r'(\d+)개월 전', date_text)
                if months_match:
                    months = int(months_match.group(1))
                    return now - timedelta(days=months * 30)
            
            elif '년 전' in date_text:
                years_match = re.search(r'(\d+)년 전', date_text)
                if years_match:
                    years = int(years_match.group(1))
                    return now - timedelta(days=years * 365)
            
            # 영어 패턴도 지원
            elif 'day' in date_text:
                days_match = re.search(r'(\d+)\s*day', date_text)
                if days_match:
                    days = int(days_match.group(1))
                    return now - timedelta(days=days)
            
            elif 'week' in date_text:
                weeks_match = re.search(r'(\d+)\s*week', date_text)
                if weeks_match:
                    weeks = int(weeks_match.group(1))
                    return now - timedelta(weeks=weeks)
            
            elif 'month' in date_text:
                months_match = re.search(r'(\d+)\s*month', date_text)
                if months_match:
                    months = int(months_match.group(1))
                    return now - timedelta(days=months * 30)
            
            elif 'year' in date_text:
                years_match = re.search(r'(\d+)\s*year', date_text)
                if years_match:
                    years = int(years_match.group(1))
                    return now - timedelta(days=years * 365)
        
        except Exception as e:
            logger.error(f"날짜 파싱 실패: {date_text} - {e}")
        
        return None
    
    def _scroll_to_load_more_reviews(self) -> bool:
        """스크롤하여 더 많은 리뷰 로드"""
        try:
            # 리뷰 컨테이너 찾기
            review_container = self.driver.find_element(
                By.CSS_SELECTOR, 
                "[data-value='Reviews'] [role='main']"
            )
            
            # 컨테이너 내에서 스크롤
            self.driver.execute_script(
                "arguments[0].scrollTop = arguments[0].scrollHeight", 
                review_container
            )
            
            self.add_delay()
            
            # "더보기" 버튼이 있으면 클릭
            try:
                more_button = self.driver.find_element(
                    By.CSS_SELECTOR, 
                    "[data-value='Reviews'] button[jsaction*='review']"
                )
                if more_button.is_displayed() and more_button.is_enabled():
                    more_button.click()
                    self.add_delay()
            except NoSuchElementException:
                pass
            
            return True
        
        except Exception as e:
            logger.error(f"스크롤 로딩 실패: {e}")
            return False
    
    def _expand_review_text(self):
        """리뷰 텍스트 전체 보기"""
        try:
            # "더보기" 버튼들 찾아서 클릭
            more_buttons = self.driver.find_elements(
                By.CSS_SELECTOR, 
                "button[data-expandable-section]"
            )
            
            for button in more_buttons:
                try:
                    if button.is_displayed():
                        self.driver.execute_script("arguments[0].click();", button)
                        time.sleep(0.5)
                except Exception:
                    continue
        
        except Exception as e:
            logger.error(f"리뷰 텍스트 확장 실패: {e}")


# 크롤러 인스턴스 생성 및 등록
def register_google_crawler():
    """구글 맵 크롤러 등록"""
    from .base import crawler_manager
    
    google_crawler = GoogleMapsCrawler()
    crawler_manager.register_crawler('google', google_crawler)
    logger.info("구글 맵 크롤러 등록 완료")


# 모듈 로드 시 자동 등록
register_google_crawler()