from rest_framework.permissions import BasePermission

# 1
class IsStaffPermission(BasePermission):
    """
    允許只有 staff 使用者訪問的權限。
    """
    def has_permission(self, request, view):
        # 檢查使用者是否已認證，且是否是 staff（或 superuser）。
        # 放寬接受 is_superuser，避免歷史上僅被賦予 is_superuser 的管理員被鎖死。
        return bool(
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
        )

# 2
class IsStaffOrCreateOnly(BasePermission):
    """
    允許只有 staff 使用者訪問的權限，但任何人可以做新增。
    """
    def has_permission(self, request, view):
        # 允許任何人執行 POST
        if view.action == 'create':
            return True
        # 其他操作需要 staff 身份
        return request.user and request.user.is_staff
