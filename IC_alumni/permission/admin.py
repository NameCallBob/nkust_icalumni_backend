from rest_framework import permissions

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    自訂權限類別：
    - 允許所有人讀取 (GET, HEAD, OPTIONS)。
    - 僅限管理員執行修改操作 (POST, PUT, DELETE)。
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user.is_staff