from rest_framework.permissions import BasePermission

class IsStaffPermission(BasePermission):
    """
    允許只有 staff 使用者訪問的權限。
    """
    def has_permission(self, request, view):
        # 檢查使用者是否已認證，且是否是 staff
        return request.user and request.user.is_authenticated and request.user.is_staff
