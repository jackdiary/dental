#!/usr/bin/env python
"""
Cloud SQL에 대량 데이터를 업로드하는 스크립트
"""
import os
import subprocess
import sys
from datetime import datetime

def run_command(command, description):
    """명령어 실행 및 결과 출력"""
    print(f"\n🔄 {description}")
    print(f"실행 명령어: {command}")
    
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} 성공")
            if result.stdout:
                print(f"출력: {result.stdout}")
            return True
        else:
            print(f"❌ {description} 실패")
            print(f"오류: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {description} 실행 중 오류: {e}")
        return False

def check_prerequisites():
    """필수 조건 확인"""
    print("🔍 필수 조건 확인 중...")
    
    # gcloud CLI 확인
    if not run_command("gcloud --version", "gcloud CLI 확인"):
        print("❌ gcloud CLI가 설치되지 않았습니다.")
        print("설치 방법: https://cloud.google.com/sdk/docs/install")
        return False
    
    # 인증 확인
    if not run_command("gcloud auth list --filter=status:ACTIVE", "Google Cloud 인증 확인"):
        print("❌ Google Cloud에 로그인되지 않았습니다.")
        print("로그인 명령어: gcloud auth login")
        return False
    
    # gcloud storage 확인
    if not run_command("gcloud storage ls", "Cloud Storage 접근 확인"):
        print("❌ Cloud Storage에 접근할 수 없습니다.")
        return False
    
    # SQL 파일 존재 확인
    if not os.path.exists("complete_database_insert.sql"):
        print("❌ complete_database_insert.sql 파일이 없습니다.")
        print("먼저 generate_sql_inserts.py를 실행해주세요.")
        return False
    
    print("✅ 모든 필수 조건이 충족되었습니다.")
    return True

def upload_to_cloud_storage():
    """Cloud Storage에 SQL 파일 업로드"""
    bucket_name = "dental-ai-2024-sql-temp"
    
    print(f"\n📤 Cloud Storage에 SQL 파일 업로드 중...")
    
    # 버킷 생성 (이미 존재하면 무시)
    run_command(
        f"gcloud storage buckets create gs://{bucket_name} --project=dental-ai-2024 --location=asia-northeast3",
        "임시 버킷 생성"
    )
    
    # SQL 파일 업로드
    if run_command(
        f"gcloud storage cp complete_database_insert.sql gs://{bucket_name}/",
        "SQL 파일 업로드"
    ):
        return bucket_name
    else:
        return None

def import_to_cloud_sql(bucket_name):
    """Cloud SQL에 데이터 임포트"""
    project_id = "dental-ai-2024"
    instance_name = "dental-ai-db"
    database_name = "dental_ai"
    
    print(f"\n🗄️ Cloud SQL에 데이터 임포트 중...")
    
    # Cloud SQL 임포트 실행
    import_command = f"""gcloud sql import sql {instance_name} \
        gs://{bucket_name}/complete_database_insert.sql \
        --database={database_name} \
        --project={project_id}"""
    
    return run_command(import_command, "Cloud SQL 데이터 임포트")

def cleanup_cloud_storage(bucket_name):
    """임시 Cloud Storage 정리"""
    print(f"\n🧹 임시 파일 정리 중...")
    
    # 파일 삭제
    run_command(
        f"gcloud storage rm gs://{bucket_name}/complete_database_insert.sql",
        "임시 SQL 파일 삭제"
    )
    
    # 버킷 삭제
    run_command(
        f"gcloud storage buckets delete gs://{bucket_name}",
        "임시 버킷 삭제"
    )

def verify_data_import():
    """데이터 임포트 확인"""
    print(f"\n🔍 데이터 임포트 확인 중...")
    
    # Cloud SQL Proxy를 통한 연결 확인
    proxy_command = """gcloud sql connect dental-ai-db \
        --user=dental_user \
        --database=dental_ai \
        --project=dental-ai-2024"""
    
    print("다음 명령어로 데이터베이스에 연결하여 확인할 수 있습니다:")
    print(f"  {proxy_command}")
    print("\n연결 후 다음 쿼리로 데이터 확인:")
    print("  SELECT COUNT(*) FROM clinics_clinic;")
    print("  SELECT COUNT(*) FROM reviews_review;")
    print("  SELECT COUNT(*) FROM analysis_sentimentanalysis;")
    print("  SELECT COUNT(*) FROM analysis_pricedata;")

def deploy_via_django():
    """Django를 통한 배포 (대안 방법)"""
    print(f"\n🐍 Django를 통한 데이터 배포 중...")
    
    # 프로덕션 환경으로 설정
    os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings.production'
    
    # 마이그레이션 실행
    if not run_command("python manage.py migrate", "데이터베이스 마이그레이션"):
        return False
    
    # 데이터 생성 스크립트 실행
    if not run_command("python create_massive_data.py", "대량 데이터 생성"):
        return False
    
    print("✅ Django를 통한 데이터 배포 완료")
    return True

def main():
    """메인 실행 함수"""
    print("🚀 Cloud SQL에 대량 치과 데이터 배포 시작")
    print("=" * 80)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 배포 방법 선택
    print("\n📋 배포 방법을 선택해주세요:")
    print("1. Cloud Storage를 통한 SQL 임포트 (권장)")
    print("2. Django 스크립트를 통한 직접 생성")
    print("3. 수동 배포 가이드만 출력")
    
    choice = input("\n선택 (1-3): ").strip()
    
    if choice == "1":
        # Cloud Storage를 통한 SQL 임포트
        if not check_prerequisites():
            return
        
        bucket_name = upload_to_cloud_storage()
        if not bucket_name:
            print("❌ Cloud Storage 업로드 실패")
            return
        
        if import_to_cloud_sql(bucket_name):
            print("✅ Cloud SQL 임포트 성공!")
            cleanup_cloud_storage(bucket_name)
            verify_data_import()
        else:
            print("❌ Cloud SQL 임포트 실패")
            cleanup_cloud_storage(bucket_name)
    
    elif choice == "2":
        # Django를 통한 직접 생성
        deploy_via_django()
    
    elif choice == "3":
        # 수동 배포 가이드
        print_manual_deployment_guide()
    
    else:
        print("❌ 잘못된 선택입니다.")
        return
    
    print("\n" + "=" * 80)
    print("✅ 배포 프로세스 완료!")
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def print_manual_deployment_guide():
    """수동 배포 가이드 출력"""
    print("\n📖 수동 배포 가이드")
    print("=" * 50)
    
    print("\n1️⃣ Cloud Storage에 SQL 파일 업로드:")
    print("gsutil mb -p dental-ai-2024 -l asia-northeast3 gs://dental-ai-2024-sql-temp")
    print("gsutil cp complete_database_insert.sql gs://dental-ai-2024-sql-temp/")
    
    print("\n2️⃣ Cloud SQL에 데이터 임포트:")
    print("gcloud sql import sql dental-ai-db \\")
    print("  gs://dental-ai-2024-sql-temp/complete_database_insert.sql \\")
    print("  --database=dental_ai \\")
    print("  --project=dental-ai-2024")
    
    print("\n3️⃣ 임포트 확인:")
    print("gcloud sql connect dental-ai-db --user=dental_user --database=dental_ai")
    print("SELECT COUNT(*) FROM clinics_clinic;  -- 510개 예상")
    print("SELECT COUNT(*) FROM reviews_review;  -- 18,288개 예상")
    
    print("\n4️⃣ 정리:")
    print("gsutil rm gs://dental-ai-2024-sql-temp/complete_database_insert.sql")
    print("gsutil rb gs://dental-ai-2024-sql-temp")
    
    print("\n5️⃣ 애플리케이션 재배포:")
    print("gcloud builds submit --config cloudbuild.yaml")

if __name__ == "__main__":
    main()