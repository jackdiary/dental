from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    관리자 권한 확인
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    객체 소유자만 수정 가능, 나머지는 읽기 전용
    """
    def has_object_permission(self, request, view, obj):
        # 읽기 권한은 모든 요청에 허용
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # 쓰기 권한은 객체 소유자에게만 허용
        return obj.user == request.user


class IsAuthenticatedOrReadOnly(permissions.BasePermission):
    """
    인증된 사용자는 모든 권한, 비인증 사용자는 읽기 전용
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated