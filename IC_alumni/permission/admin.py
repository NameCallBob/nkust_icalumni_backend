from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    自訂權限類別：管理員可執行任何操作，其他用戶僅能進行讀取操作。
    """

    def has_permission(self, request, view):
        # 允許讀取操作
        if request.method in permissions.SAFE_METHODS:
            return True
        # 僅管理員可進行其他操作
        return request.user and request.user.is_staff
