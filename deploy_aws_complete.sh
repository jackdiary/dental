#!/bin/bash

# AWS EC2 배포 스크립트
# 사용법: ./deploy_aws_complete.sh

set -e  # 에러 발생 시 스크립트 중단

echo "🚀 AWS EC2 배포 시작..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. 환경 변수 확인
echo -e "${YELLOW}📋 1. 환경 변수 확인...${NC}"
if [ ! -f .env.aws ]; then
    echo -e "${RED}❌ .env.aws 파일이 없습니다!${NC}"
    exit 1
fi
echo -e "${GREEN}✅ .env.aws 파일 확인 완료${NC}"

# 2. 기존 컨테이너 중지 및 제거
echo -e "${YELLOW}📋 2. 기존 컨테이너 중지 및 제거...${NC}"
sudo docker compose -f docker-compose.aws.yml down -v || true
echo -e "${GREEN}✅ 기존 컨테이너 정리 완료${NC}"

# 3. Docker 이미지 빌드
echo -e "${YELLOW}📋 3. Docker 이미지 빌드...${NC}"
sudo docker compose -f docker-compose.aws.yml build --no-cache
echo -e "${GREEN}✅ Docker 이미지 빌드 완료${NC}"

# 4. 데이터베이스 및 Redis 시작
echo -e "${YELLOW}📋 4. 데이터베이스 및 Redis 시작...${NC}"
sudo docker compose -f docker-compose.aws.yml up -d db redis
echo "⏳ 데이터베이스 준비 대기 중..."
sleep 10
echo -e "${GREEN}✅ 데이터베이스 및 Redis 시작 완료${NC}"

# 5. 데이터베이스 마이그레이션
echo -e "${YELLOW}📋 5. 데이터베이스 마이그레이션...${NC}"
sudo docker compose -f docker-compose.aws.yml run --rm web python manage.py migrate
echo -e "${GREEN}✅ 마이그레이션 완료${NC}"

# 6. 정적 파일 수집
echo -e "${YELLOW}📋 6. 정적 파일 수집...${NC}"
sudo docker compose -f docker-compose.aws.yml run --rm web python manage.py collectstatic --noinput
echo -e "${GREEN}✅ 정적 파일 수집 완료${NC}"

# 7. 슈퍼유저 생성 (선택사항)
echo -e "${YELLOW}📋 7. 슈퍼유저 생성 (선택사항)...${NC}"
read -p "슈퍼유저를 생성하시겠습니까? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    sudo docker compose -f docker-compose.aws.yml run --rm web python manage.py createsuperuser
    echo -e "${GREEN}✅ 슈퍼유저 생성 완료${NC}"
else
    echo -e "${YELLOW}⏭️  슈퍼유저 생성 건너뛰기${NC}"
fi

# 8. 모든 서비스 시작
echo -e "${YELLOW}📋 8. 모든 서비스 시작...${NC}"
sudo docker compose -f docker-compose.aws.yml up -d
echo -e "${GREEN}✅ 모든 서비스 시작 완료${NC}"

# 9. 서비스 상태 확인
echo -e "${YELLOW}📋 9. 서비스 상태 확인...${NC}"
sleep 5
sudo docker compose -f docker-compose.aws.yml ps
echo -e "${GREEN}✅ 서비스 상태 확인 완료${NC}"

# 10. 로그 확인
echo -e "${YELLOW}📋 10. 웹 서비스 로그 확인...${NC}"
sudo docker compose -f docker-compose.aws.yml logs --tail=50 web

# 완료 메시지
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 배포 완료!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "📍 서비스 접속 정보:"
echo -e "   - 백엔드 API: ${GREEN}http://3.36.129.103:8000${NC}"
echo -e "   - 관리자 페이지: ${GREEN}http://3.36.129.103:8000/admin${NC}"
echo -e "   - API 문서: ${GREEN}http://3.36.129.103:8000/api/docs${NC}"
echo ""
echo -e "📊 유용한 명령어:"
echo -e "   - 로그 확인: ${YELLOW}sudo docker compose -f docker-compose.aws.yml logs -f web${NC}"
echo -e "   - 서비스 재시작: ${YELLOW}sudo docker compose -f docker-compose.aws.yml restart web${NC}"
echo -e "   - 서비스 중지: ${YELLOW}sudo docker compose -f docker-compose.aws.yml down${NC}"
echo -e "   - 컨테이너 접속: ${YELLOW}sudo docker exec -it hosptal-web bash${NC}"
echo ""
