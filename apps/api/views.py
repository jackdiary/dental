from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from config.cors_settings import CORSDebugger

# Create your views here.

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    API 상태 확인 엔드포인트
    데이터베이스, 캐시 연결 상태를 확인합니다.
    """
    import time
    from django.db import connection
    from django.core.cache import cache
    from django.conf import settings
    
    start_time = time.time()
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'environment': getattr(settings, 'ENVIRONMENT', 'unknown'),
        'checks': {}
    }
    
    try:
        # 데이터베이스 연결 확인
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        health_status['checks']['database'] = 'healthy'
    except Exception as e:
        health_status['checks']['database'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    try:
        # Redis 캐시 연결 확인
        cache.set('health_check', 'ok', 10)
        cache_value = cache.get('health_check')
        if cache_value == 'ok':
            health_status['checks']['cache'] = 'healthy'
        else:
            health_status['checks']['cache'] = 'unhealthy: cache test failed'
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['checks']['cache'] = f'unhealthy: {str(e)}'
        health_status['status'] = 'degraded'
    
    # 응답 시간 측정
    health_status['response_time_ms'] = round((time.time() - start_time) * 1000, 2)
    
    # 상태에 따른 HTTP 상태 코드 설정
    if health_status['status'] == 'healthy':
        status_code = status.HTTP_200_OK
    elif health_status['status'] == 'degraded':
        status_code = status.HTTP_200_OK  # 부분적 문제는 200으로 처리
    else:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    return Response(health_status, status=status_code)


@api_view(['GET', 'OPTIONS'])
@permission_classes([AllowAny])
def cors_health_check(request):
    """
    CORS 설정 상태 확인 엔드포인트
    현재 CORS 설정과 요청 헤더를 분석합니다.
    """
    import time
    from django.conf import settings
    
    start_time = time.time()
    
    # CORS 디버거를 사용하여 헬스 체크 데이터 생성
    cors_health_data = CORSDebugger.create_health_check_data()
    
    # 요청 정보 추가
    request_info = {
        'method': request.method,
        'origin': request.META.get('HTTP_ORIGIN'),
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'referer': request.META.get('HTTP_REFERER'),
        'host': request.META.get('HTTP_HOST'),
        'remote_addr': request.META.get('REMOTE_ADDR'),
        'forwarded_for': request.META.get('HTTP_X_FORWARDED_FOR'),
    }
    
    # CORS 관련 헤더 정보
    cors_headers = {}
    for key, value in request.META.items():
        if key.startswith('HTTP_') and ('ORIGIN' in key or 'CORS' in key or 'ACCESS_CONTROL' in key):
            cors_headers[key] = value
    
    # 응답 데이터 구성
    health_response = {
        'status': 'healthy' if cors_health_data['is_valid'] else 'unhealthy',
        'timestamp': time.time(),
        'cors_config': cors_health_data,
        'request_info': request_info,
        'cors_headers': cors_headers,
        'response_time_ms': round((time.time() - start_time) * 1000, 2),
    }
    
    # 검증 오류가 있으면 경고 상태로 설정
    if cors_health_data['validation_errors']:
        health_response['status'] = 'warning'
        health_response['warnings'] = cors_health_data['validation_errors']
    
    # 상태에 따른 HTTP 상태 코드 설정
    if health_response['status'] == 'healthy':
        status_code = status.HTTP_200_OK
    elif health_response['status'] == 'warning':
        status_code = status.HTTP_200_OK  # 경고는 200으로 처리
    else:
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    
    response = Response(health_response, status=status_code)
    
    # CORS 디버깅을 위한 응답 헤더 검증
    if request.method == 'OPTIONS':
        # 프리플라이트 요청에 대한 추가 정보
        response.data['preflight_request'] = True
        response.data['preflight_headers'] = {
            'Access-Control-Request-Method': request.META.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD'),
            'Access-Control-Request-Headers': request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS'),
        }
    
    return response