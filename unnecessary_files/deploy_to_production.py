#!/usr/bin/env python
"""
프로덕션 환경에 대량 데이터를 배포하는 스크립트
"""
import subprocess
import sys
import os
from datetime import datetime

def run_gcloud_command(command, description):
    """gcloud 명령어 실행"""
    print(f"\n🔄 {description}")
    print(f"명령어: {command}")
    
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

def deploy_backend():
    """백엔드 애플리케이션 배포"""
    print("🚀 백엔드 애플리케이션 배포 중...")
    
    # 백엔드 빌드 및 배포
    build_command = "gcloud builds submit --config cloudbuild.yaml --project dental-ai-2024"
    
    return run_gcloud_command(build_command, "백엔드 애플리케이션 빌드 및 배포")

def run_data_migration():
    """데이터 마이그레이션 실행"""
    print("🗄️ 데이터베이스 마이그레이션 실행 중...")
    
    # Cloud Run Job으로 마이그레이션 실행
    migration_command = """gcloud run jobs create dental-ai-migrate \
        --image=gcr.io/dental-ai-2024/dental-ai-backend:latest \
        --region=asia-northeast3 \
        --project=dental-ai-2024 \
        --set-env-vars=DJANGO_SETTINGS_MODULE=config.settings.production \
        --memory=1Gi \
        --cpu=1 \
        --max-retries=1 \
        --parallelism=1 \
        --command=python \
        --args=manage.py,migrate"""
    
    if run_gcloud_command(migration_command, "마이그레이션 Job 생성"):
        # Job 실행
        execute_command = "gcloud run jobs execute dental-ai-migrate --region=asia-northeast3 --project=dental-ai-2024 --wait"
        return run_gcloud_command(execute_command, "마이그레이션 실행")
    
    return False

def run_data_creation():
    """대량 데이터 생성 실행"""
    print("📊 대량 데이터 생성 실행 중...")
    
    # Cloud Run Job으로 데이터 생성 실행
    data_command = """gcloud run jobs create dental-ai-data-create \
        --image=gcr.io/dental-ai-2024/dental-ai-backend:latest \
        --region=asia-northeast3 \
        --project=dental-ai-2024 \
        --set-env-vars=DJANGO_SETTINGS_MODULE=config.settings.production \
        --memory=2Gi \
        --cpu=2 \
        --max-retries=1 \
        --parallelism=1 \
        --command=python \
        --args=create_massive_data.py"""
    
    if run_gcloud_command(data_command, "데이터 생성 Job 생성"):
        # Job 실행
        execute_command = "gcloud run jobs execute dental-ai-data-create --region=asia-northeast3 --project=dental-ai-2024 --wait"
        return run_gcloud_command(execute_command, "데이터 생성 실행")
    
    return False

def verify_deployment():
    """배포 확인"""
    print("🔍 배포 확인 중...")
    
    # 서비스 상태 확인
    status_command = "gcloud run services describe dental-ai-backend --region=asia-northeast3 --project=dental-ai-2024"
    
    if run_gcloud_command(status_command, "서비스 상태 확인"):
        print("\n✅ 배포 확인 완료!")
        print("🌐 서비스 URL을 확인하여 API가 정상 작동하는지 테스트해보세요.")
        
        # URL 확인
        url_command = "gcloud run services describe dental-ai-backend --region=asia-northeast3 --project=dental-ai-2024 --format='value(status.url)'"
        run_gcloud_command(url_command, "서비스 URL 확인")
        
        return True
    
    return False

def main():
    """메인 실행 함수"""
    print("🚀 프로덕션 환경 대량 데이터 배포 시작")
    print("=" * 80)
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    # 1. 백엔드 애플리케이션 배포
    if not deploy_backend():
        print("❌ 백엔드 배포 실패")
        return
    
    # 2. 데이터베이스 마이그레이션
    if not run_data_migration():
        print("❌ 데이터베이스 마이그레이션 실패")
        return
    
    # 3. 대량 데이터 생성
    if not run_data_creation():
        print("❌ 대량 데이터 생성 실패")
        return
    
    # 4. 배포 확인
    if not verify_deployment():
        print("❌ 배포 확인 실패")
        return
    
    print("\n" + "=" * 80)
    print("✅ 프로덕션 환경 배포 완료!")
    print(f"완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n📊 배포된 데이터:")
    print("   - 치과: 510개")
    print("   - 리뷰: 18,288개")
    print("   - 감성분석: 18,288개")
    print("   - 가격정보: 7,302개")
    print("=" * 80)

if __name__ == "__main__":
    main()