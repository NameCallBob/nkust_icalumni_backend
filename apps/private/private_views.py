from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import BasePermission
from apps.private.models import Private
from apps.private.serializer import PrivateSerializer
from django.db.models import Q

# 自訂權限：僅允許管理員操作
class IsAdminUser(BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)

class PrivateViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminUser]

    # 查詢所有 Private 資料
    def list(self, request):
        private_users = Private.objects.all()
        serializer = PrivateSerializer(private_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 根據自訂參數查詢單一 Private
    @action(detail=False, methods=['get'], url_path='query')
    def get_account(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({"detail": "請提供 email 作為查詢參數。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            private_user = Private.objects.get(email=email)
            serializer = PrivateSerializer(private_user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Private.DoesNotExist:
            return Response({"detail": "找不到對應的使用者。"}, status=status.HTTP_404_NOT_FOUND)

    # 更新現有的 Private
    @action(detail=False, methods=['put'], url_path='update')
    def update_private(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "請提供 email 作為更新參數。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            private_user = Private.objects.get(email=email)
            serializer = PrivateSerializer(private_user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Private.DoesNotExist:
            return Response({"detail": "找不到對應的使用者。"}, status=status.HTTP_404_NOT_FOUND)

    # 刪除指定的 Private
    @action(detail=False, methods=['delete'], url_path='delete')
    def remove(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "請提供 email 作為刪除參數。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            private_user = Private.objects.get(email=email)
            private_user.delete()
            return Response({"detail": f"已成功刪除 email 為 {email} 的使用者。"}, status=status.HTTP_204_NO_CONTENT)
        except Private.DoesNotExist:
            return Response({"detail": "找不到對應的使用者。"}, status=status.HTTP_404_NOT_FOUND)
        
    # 單一條件查詢
    @action(detail=False, methods=['get'], url_path='filter')
    def filter_private(self, request):
        filters = {}
        for field in ['email', 'is_active', 'is_staff', 'is_superuser']:
            if value := request.query_params.get(field):
                filters[field] = value
        private_users = Private.objects.filter(**filters)
        serializer = PrivateSerializer(private_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 模糊查詢所有欄位
    @action(detail=False, methods=['get'], url_path='search')
    def search_private(self, request):
        query = request.query_params.get('query')
        if not query:
            return Response({"detail": "請提供 query 作為搜尋參數。"}, status=status.HTTP_400_BAD_REQUEST)
        private_users = Private.objects.filter(
            Q(email__icontains=query) |
            Q(is_active__icontains=query) |
            Q(is_staff__icontains=query) |
            Q(is_superuser__icontains=query)
        )
        serializer = PrivateSerializer(private_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # 帳號啟用/停用
    @action(detail=False, methods=['post'], url_path='toggle-active')
    def toggle_active(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "請提供 email 作為參數。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            private_user = Private.objects.get(email=email)
            private_user.is_active = not private_user.is_active
            private_user.save()
            status_msg = "啟用" if private_user.is_active else "停用"
            return Response({"detail": f"帳號已{status_msg}。"}, status=status.HTTP_200_OK)
        except Private.DoesNotExist:
            return Response({"detail": "找不到對應的使用者。"}, status=status.HTTP_404_NOT_FOUND)

    # 帳號權限調整
    @action(detail=False, methods=['post'], url_path='adjust-account')
    def adjust_account(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"detail": "請提供 email 作為參數。"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            private_user = Private.objects.get(email=email)
            is_staff = request.data.get('is_staff')
            is_superuser = request.data.get('is_superuser')

            if is_staff is not None:
                private_user.is_staff = is_staff
            if is_superuser is not None:
                private_user.is_superuser = is_superuser

            private_user.save()
            return Response({"detail": "帳號權限已更新。"}, status=status.HTTP_200_OK)
        except Private.DoesNotExist:
            return Response({"detail": "找不到對應的使用者。"}, status=status.HTTP_404_NOT_FOUND)
