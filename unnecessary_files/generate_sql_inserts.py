#!/usr/bin/env python
"""
생성된 데이터를 SQL INSERT 문으로 변환하는 스크립트
"""
import os
import sys
import django
from datetime import datetime

# Django 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.clinics.models import Clinic
from apps.reviews.models import Review
from apps.analysis.models import SentimentAnalysis, PriceData

def escape_sql_string(text):
    """SQL 문자열 이스케이프 처리"""
    if text is None:
        return 'NULL'
    # 작은따옴표를 두 개로 변경하여 이스케이프
    escaped = str(text).replace("'", "''")
    return f"'{escaped}'"

def generate_clinics_sql():
    """치과 데이터 SQL INSERT 문 생성"""
    print("🏥 치과 데이터 SQL 생성 중...")
    
    clinics = Clinic.objects.all().order_by('id')
    
    with open('sql_insert_clinics.sql', 'w', encoding='utf-8') as f:
        f.write("-- 치과 데이터 INSERT 문\n")
        f.write(f"-- 총 {clinics.count()}개 치과\n")
        f.write(f"-- 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 테이블 초기화
        f.write("-- 기존 데이터 삭제\n")
        f.write("DELETE FROM clinics_clinic;\n\n")
        
        # INSERT 문 생성
        f.write("-- 치과 데이터 삽입\n")
        f.write("INSERT INTO clinics_clinic (\n")
        f.write("    id, name, address, district, latitude, longitude, phone,\n")
        f.write("    has_parking, night_service, weekend_service, specialties,\n")
        f.write("    description, business_hours, is_verified, total_reviews, average_rating\n")
        f.write(") VALUES\n")
        
        for i, clinic in enumerate(clinics):
            f.write(f"({clinic.id}, ")
            f.write(f"{escape_sql_string(clinic.name)}, ")
            f.write(f"{escape_sql_string(clinic.address)}, ")
            f.write(f"{escape_sql_string(clinic.district)}, ")
            f.write(f"{clinic.latitude}, ")
            f.write(f"{clinic.longitude}, ")
            f.write(f"{escape_sql_string(clinic.phone)}, ")
            f.write(f"{'TRUE' if clinic.has_parking else 'FALSE'}, ")
            f.write(f"{'TRUE' if clinic.night_service else 'FALSE'}, ")
            f.write(f"{'TRUE' if clinic.weekend_service else 'FALSE'}, ")
            f.write(f"{escape_sql_string(clinic.specialties)}, ")
            f.write(f"{escape_sql_string(clinic.description)}, ")
            f.write(f"{escape_sql_string(clinic.business_hours)}, ")
            f.write(f"{'TRUE' if clinic.is_verified else 'FALSE'}, ")
            f.write(f"{clinic.total_reviews or 0}, ")
            f.write(f"{clinic.average_rating or 0}")
            
            if i < clinics.count() - 1:
                f.write("),\n")
            else:
                f.write(");\n\n")
        
        # 시퀀스 재설정 (PostgreSQL용)
        f.write("-- 시퀀스 재설정 (PostgreSQL)\n")
        f.write(f"SELECT setval('clinics_clinic_id_seq', {clinics.count()});\n\n")
    
    print(f"✅ 치과 SQL 생성 완료: sql_insert_clinics.sql ({clinics.count()}개)")

def generate_reviews_sql():
    """리뷰 데이터 SQL INSERT 문 생성"""
    print("📝 리뷰 데이터 SQL 생성 중...")
    
    reviews = Review.objects.all().order_by('id')
    
    with open('sql_insert_reviews.sql', 'w', encoding='utf-8') as f:
        f.write("-- 리뷰 데이터 INSERT 문\n")
        f.write(f"-- 총 {reviews.count()}개 리뷰\n")
        f.write(f"-- 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 테이블 초기화
        f.write("-- 기존 데이터 삭제\n")
        f.write("DELETE FROM reviews_review;\n\n")
        
        # INSERT 문 생성 (배치 처리)
        batch_size = 1000
        total_batches = (reviews.count() + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, reviews.count())
            batch_reviews = reviews[start_idx:end_idx]
            
            f.write(f"-- 배치 {batch_num + 1}/{total_batches} ({start_idx + 1}-{end_idx})\n")
            f.write("INSERT INTO reviews_review (\n")
            f.write("    id, clinic_id, source, original_text, processed_text,\n")
            f.write("    original_rating, review_date, reviewer_hash, external_id,\n")
            f.write("    is_processed, is_duplicate\n")
            f.write(") VALUES\n")
            
            for i, review in enumerate(batch_reviews):
                f.write(f"({review.id}, ")
                f.write(f"{review.clinic_id}, ")
                f.write(f"{escape_sql_string(review.source)}, ")
                f.write(f"{escape_sql_string(review.original_text)}, ")
                f.write(f"{escape_sql_string(review.processed_text)}, ")
                f.write(f"{review.original_rating}, ")
                f.write(f"'{review.review_date.strftime('%Y-%m-%d %H:%M:%S')}', ")
                f.write(f"{escape_sql_string(review.reviewer_hash)}, ")
                f.write(f"{escape_sql_string(review.external_id)}, ")
                f.write(f"{'TRUE' if review.is_processed else 'FALSE'}, ")
                f.write(f"{'TRUE' if review.is_duplicate else 'FALSE'}")
                
                if i < len(batch_reviews) - 1:
                    f.write("),\n")
                else:
                    f.write(");\n\n")
        
        # 시퀀스 재설정 (PostgreSQL용)
        f.write("-- 시퀀스 재설정 (PostgreSQL)\n")
        f.write(f"SELECT setval('reviews_review_id_seq', {reviews.count()});\n\n")
    
    print(f"✅ 리뷰 SQL 생성 완료: sql_insert_reviews.sql ({reviews.count()}개)")

def generate_sentiment_analysis_sql():
    """감성분석 데이터 SQL INSERT 문 생성"""
    print("🧠 감성분석 데이터 SQL 생성 중...")
    
    analyses = SentimentAnalysis.objects.all().order_by('id')
    
    with open('sql_insert_sentiment_analysis.sql', 'w', encoding='utf-8') as f:
        f.write("-- 감성분석 데이터 INSERT 문\n")
        f.write(f"-- 총 {analyses.count()}개 분석\n")
        f.write(f"-- 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 테이블 초기화
        f.write("-- 기존 데이터 삭제\n")
        f.write("DELETE FROM analysis_sentimentanalysis;\n\n")
        
        # INSERT 문 생성 (배치 처리)
        batch_size = 1000
        total_batches = (analyses.count() + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, analyses.count())
            batch_analyses = analyses[start_idx:end_idx]
            
            f.write(f"-- 배치 {batch_num + 1}/{total_batches} ({start_idx + 1}-{end_idx})\n")
            f.write("INSERT INTO analysis_sentimentanalysis (\n")
            f.write("    id, review_id, price_score, skill_score, kindness_score,\n")
            f.write("    waiting_time_score, facility_score, overtreatment_score,\n")
            f.write("    model_version, confidence_score\n")
            f.write(") VALUES\n")
            
            for i, analysis in enumerate(batch_analyses):
                f.write(f"({analysis.id}, ")
                f.write(f"{analysis.review_id}, ")
                f.write(f"{analysis.price_score}, ")
                f.write(f"{analysis.skill_score}, ")
                f.write(f"{analysis.kindness_score}, ")
                f.write(f"{analysis.waiting_time_score}, ")
                f.write(f"{analysis.facility_score}, ")
                f.write(f"{analysis.overtreatment_score}, ")
                f.write(f"{escape_sql_string(analysis.model_version)}, ")
                f.write(f"{analysis.confidence_score}")
                
                if i < len(batch_analyses) - 1:
                    f.write("),\n")
                else:
                    f.write(");\n\n")
        
        # 시퀀스 재설정 (PostgreSQL용)
        f.write("-- 시퀀스 재설정 (PostgreSQL)\n")
        f.write(f"SELECT setval('analysis_sentimentanalysis_id_seq', {analyses.count()});\n\n")
    
    print(f"✅ 감성분석 SQL 생성 완료: sql_insert_sentiment_analysis.sql ({analyses.count()}개)")

def generate_price_data_sql():
    """가격 데이터 SQL INSERT 문 생성"""
    print("💰 가격 데이터 SQL 생성 중...")
    
    prices = PriceData.objects.all().order_by('id')
    
    with open('sql_insert_price_data.sql', 'w', encoding='utf-8') as f:
        f.write("-- 가격 데이터 INSERT 문\n")
        f.write(f"-- 총 {prices.count()}개 가격 정보\n")
        f.write(f"-- 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # 테이블 초기화
        f.write("-- 기존 데이터 삭제\n")
        f.write("DELETE FROM analysis_pricedata;\n\n")
        
        # INSERT 문 생성 (배치 처리)
        batch_size = 1000
        total_batches = (prices.count() + batch_size - 1) // batch_size
        
        for batch_num in range(total_batches):
            start_idx = batch_num * batch_size
            end_idx = min((batch_num + 1) * batch_size, prices.count())
            batch_prices = prices[start_idx:end_idx]
            
            f.write(f"-- 배치 {batch_num + 1}/{total_batches} ({start_idx + 1}-{end_idx})\n")
            f.write("INSERT INTO analysis_pricedata (\n")
            f.write("    id, clinic_id, review_id, treatment_type, price,\n")
            f.write("    currency, extraction_confidence, extraction_method\n")
            f.write(") VALUES\n")
            
            for i, price in enumerate(batch_prices):
                f.write(f"({price.id}, ")
                f.write(f"{price.clinic_id}, ")
                f.write(f"{price.review_id}, ")
                f.write(f"{escape_sql_string(price.treatment_type)}, ")
                f.write(f"{price.price}, ")
                f.write(f"{escape_sql_string(price.currency)}, ")
                f.write(f"{price.extraction_confidence}, ")
                f.write(f"{escape_sql_string(price.extraction_method)}")
                
                if i < len(batch_prices) - 1:
                    f.write("),\n")
                else:
                    f.write(");\n\n")
        
        # 시퀀스 재설정 (PostgreSQL용)
        f.write("-- 시퀀스 재설정 (PostgreSQL)\n")
        f.write(f"SELECT setval('analysis_pricedata_id_seq', {prices.count()});\n\n")
    
    print(f"✅ 가격 데이터 SQL 생성 완료: sql_insert_price_data.sql ({prices.count()}개)")

def generate_complete_sql():
    """모든 데이터를 하나의 SQL 파일로 통합"""
    print("📋 통합 SQL 파일 생성 중...")
    
    with open('complete_database_insert.sql', 'w', encoding='utf-8') as f:
        f.write("-- 치과 AI 서비스 전체 데이터 INSERT 문\n")
        f.write(f"-- 생성일시: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("-- 총 데이터: 치과 510개, 리뷰 18,288개, 감성분석 18,288개, 가격 7,302개\n\n")
        
        f.write("-- ========================================\n")
        f.write("-- 1. 기존 데이터 모두 삭제\n")
        f.write("-- ========================================\n")
        f.write("DELETE FROM analysis_pricedata;\n")
        f.write("DELETE FROM analysis_sentimentanalysis;\n")
        f.write("DELETE FROM reviews_review;\n")
        f.write("DELETE FROM clinics_clinic;\n\n")
        
        # 각 SQL 파일 내용 포함
        sql_files = [
            'sql_insert_clinics.sql',
            'sql_insert_reviews.sql', 
            'sql_insert_sentiment_analysis.sql',
            'sql_insert_price_data.sql'
        ]
        
        for sql_file in sql_files:
            if os.path.exists(sql_file):
                f.write(f"-- ========================================\n")
                f.write(f"-- {sql_file} 내용\n")
                f.write(f"-- ========================================\n")
                
                with open(sql_file, 'r', encoding='utf-8') as source:
                    content = source.read()
                    # 헤더 주석과 DELETE 문 제거
                    lines = content.split('\n')
                    skip_until_insert = True
                    for line in lines:
                        if 'INSERT INTO' in line:
                            skip_until_insert = False
                        if not skip_until_insert:
                            f.write(line + '\n')
                f.write("\n")
        
        f.write("-- ========================================\n")
        f.write("-- 완료 메시지\n")
        f.write("-- ========================================\n")
        f.write("-- 모든 데이터 삽입 완료!\n")
    
    print("✅ 통합 SQL 파일 생성 완료: complete_database_insert.sql")

def main():
    """모든 SQL 생성 실행"""
    print("🚀 데이터를 SQL INSERT 문으로 변환 시작...")
    print("=" * 80)
    
    # 1. 치과 데이터 SQL 생성
    generate_clinics_sql()
    
    # 2. 리뷰 데이터 SQL 생성
    generate_reviews_sql()
    
    # 3. 감성분석 데이터 SQL 생성
    generate_sentiment_analysis_sql()
    
    # 4. 가격 데이터 SQL 생성
    generate_price_data_sql()
    
    # 5. 통합 SQL 파일 생성
    generate_complete_sql()
    
    print("=" * 80)
    print("✅ 모든 SQL INSERT 문 생성 완료!")
    print("📁 생성된 SQL 파일:")
    print("   - sql_insert_clinics.sql (치과 데이터)")
    print("   - sql_insert_reviews.sql (리뷰 데이터)")
    print("   - sql_insert_sentiment_analysis.sql (감성분석)")
    print("   - sql_insert_price_data.sql (가격 정보)")
    print("   - complete_database_insert.sql (전체 통합)")
    print()
    print("💡 사용 방법:")
    print("   1. PostgreSQL: psql -d database_name -f complete_database_insert.sql")
    print("   2. MySQL: mysql -u username -p database_name < complete_database_insert.sql")
    print("   3. 개별 파일 실행도 가능합니다.")
    print("=" * 80)

if __name__ == '__main__':
    main()