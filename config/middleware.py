"""
커스텀 미들웨어 모듈
CORS 요청 로깅 및 모니터링 기능 제공
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin
from config.cors_settings import CORSDebugger

logger = logging.getLogger(__name__)


class CORSLoggingMiddleware(MiddlewareMixin):
    """CORS 요청을 로깅하는 미들웨어"""
    
    def process_request(self, request):
        """요청 처리 시작 시 CORS 관련 정보 로깅"""
        # CORS 요청인지 확인
        origin = request.META.get('HTTP_ORIGIN')
        if origin:
            request._cors_start_time = time.time()
            request._cors_origin = origin
            
            # CORS 요청 로깅
            logger.info(f"CORS 요청 시작: {request.method} {request.path} from {origin}")
            
            # 프리플라이트 요청 감지
            if request.method == 'OPTIONS':
                request_method = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_METHOD')
                request_headers = request.META.get('HTTP_ACCESS_CONTROL_REQUEST_HEADERS')
                logger.info(f"프리플라이트 요청: Method={request_method}, Headers={request_headers}")
        
        return None
    
    def process_response(self, request, response):
        """응답 처리 시 CORS 헤더 검증 및 로깅"""
        # CORS 요청이었다면 응답 로깅
        if hasattr(request, '_cors_origin'):
            origin = request._cors_origin
            start_time = getattr(request, '_cors_start_time', time.time())
            duration = round((time.time() - start_time) * 1000, 2)
            
            # CORS 헤더 검증
            cors_validation = CORSDebugger.validate_cors_headers(response)
            
            # 응답 로깅
            logger.info(f"CORS 응답 완료: {request.method} {request.path} "
                       f"from {origin} - {response.status_code} ({duration}ms)")
            
            if cors_validation['has_cors_headers']:
                logger.debug(f"CORS 헤더: {cors_validation['cors_headers']}")
            else:
                logger.warning(f"CORS 헤더 누락: {request.path} from {origin}")
            
            # CORS 오류 감지
            if response.status_code >= 400:
                logger.error(f"CORS 요청 실패: {request.method} {request.path} "
                           f"from {origin} - {response.status_code}")
        
        return response
    
    def process_exception(self, request, exception):
        """예외 발생 시 CORS 관련 오류 로깅"""
        if hasattr(request, '_cors_origin'):
            origin = request._cors_origin
            logger.error(f"CORS 요청 중 예외 발생: {request.method} {request.path} "
                        f"from {origin} - {type(exception).__name__}: {str(exception)}")
        
        return None


class CORSSecurityMiddleware(MiddlewareMixin):
    """CORS 보안 검사 미들웨어"""
    
    def __init__(self, get_response):
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request):
        """요청의 보안성 검사"""
        origin = request.META.get('HTTP_ORIGIN')
        
        if origin:
            # 의심스러운 오리진 패턴 검사
            suspicious_patterns = [
                'localhost:',
                '127.0.0.1:',
                'file://',
                'data:',
                'javascript:',
            ]
            
            # 프로덕션 환경에서 localhost 요청 감지
            from config.cors_settings import EnvironmentDetector
            if EnvironmentDetector.is_production():
                for pattern in suspicious_patterns[:2]:  # localhost 패턴만 체크
                    if pattern in origin.lower():
                        logger.warning(f"프로덕션 환경에서 localhost 오리진 감지: {origin} "
                                     f"from {request.META.get('REMOTE_ADDR')}")
            
            # 악성 오리진 패턴 검사
            for pattern in suspicious_patterns[2:]:  # 위험한 프로토콜 체크
                if origin.lower().startswith(pattern):
                    logger.error(f"위험한 오리진 프로토콜 감지: {origin} "
                               f"from {request.META.get('REMOTE_ADDR')}")
        
        return None