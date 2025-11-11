# 🖥️ 서버에서 실행할 명령어 체크리스트

## ✅ 현재 상태
- ✅ 서버 접속 완료
- ✅ 프로젝트 클론 완료 (`/home/ubuntu/hosptal`)
- ✅ Docker 설치 완료
- ✅ 파일들이 제대로 마운트됨

## 🚀 지금 바로 실행하세요!

### 1. 프로젝트 디렉토리로 이동
```bash
cd /home/ubuntu/hosptal
```

### 2. 최신 코드 가져오기
```bash
git pull origin main
```

### 3. 배포 스크립트에 실행 권한 부여
```bash
chmod +x deploy_aws_complete.sh quick_deploy.sh
```

### 4. 자동 배포 실행
```bash
./deploy_aws_complete.sh
```

이 스크립트가 다음을 자동으로 수행합니다:
- 환경 변수 확인
- 기존 컨테이너 정리
- Docker 이미지 빌드
- 데이터베이스 및 Redis 시작
- 마이그레이션 실행
- 정적 파일 수집
- 모든 서비스 시작
- 상태 확인

### 5. 서비스 확인

배포가 완료되면 다음 명령어로 확인:

```bash
# 컨테이너 상태 확인
sudo docker compose -f docker-compose.aws.yml ps

# 웹 서비스 로그 확인
sudo docker compose -f docker-compose.aws.yml logs -f web
```

브라우저에서 접속:
- http://3.36.129.103:8000
- http://3.36.129.103:8000/api/health/
- http://3.36.129.103:8000/admin

## 🔧 문제 발생 시

### 로그 확인
```bash
sudo docker compose -f docker-compose.aws.yml logs web
```

### 컨테이너 재시작
```bash
sudo docker compose -f docker-compose.aws.yml restart web
```

### 완전 재시작
```bash
sudo docker compose -f docker-compose.aws.yml down
sudo docker compose -f docker-compose.aws.yml up -d
```

### 컨테이너 내부 접속
```bash
sudo docker exec -it hosptal-web bash
```

## 📝 슈퍼유저 생성 (선택사항)

관리자 페이지 접속을 위해:

```bash
sudo docker compose -f docker-compose.aws.yml exec web python manage.py createsuperuser
```

## 🎯 다음 단계

1. ✅ 배포 완료 확인
2. 🔐 슈퍼유저 생성
3. 🌐 브라우저에서 접속 테스트
4. 📊 API 엔드포인트 테스트
5. 🔒 보안 설정 강화 (SECRET_KEY, DB_PASSWORD 변경)

## 💡 유용한 명령어

```bash
# 실시간 로그 보기
sudo docker compose -f docker-compose.aws.yml logs -f

# 특정 서비스만 재시작
sudo docker compose -f docker-compose.aws.yml restart web

# 리소스 사용량 확인
sudo docker stats

# 디스크 사용량 확인
df -h

# 메모리 사용량 확인
free -h
```

## 🔄 코드 업데이트 시

```bash
cd /home/ubuntu/hosptal
git pull origin main
./quick_deploy.sh
```

---

**준비 완료! 이제 `./deploy_aws_complete.sh`를 실행하세요!** 🚀
