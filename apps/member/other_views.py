# views.py
from rest_framework import viewsets, status , permissions
from rest_framework.response import Response
from rest_framework.decorators import action , authentication_classes , permission_classes
from apps.member.models import Position, Graduate
from apps.member.serializer import PositionSerializer, GraduateSerializer
from django.shortcuts import get_object_or_404
from apps.private.cookie_auth import CookieJWTAuthentication as JWTAuthentication  # [資安修補 SEC-015] alias 成 cookie-aware 版本，向下相容 header 認證
from IC_alumni.permission.staff import IsStaffPermission

class PositionViewSet(viewsets.ViewSet):
    """

    """

    @action(detail=False, methods=['get'], url_path='get-all' ,authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_all(self, request):
        queryset = Position.objects.all()
        serializer = PositionSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='show-page' ,authentication_classes=[],permission_classes=[permissions.AllowAny])
    def show_page(self, request):
        queryset = Position.objects.filter(priority__lt=5)
        serializer = PositionSerializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='create-new',authentication_classes=[JWTAuthentication],permission_classes=[IsStaffPermission])
    def create_new(self, request):
        serializer = PositionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='get-one',authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_one(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({'detail': '缺少 id 参数'}, status=status.HTTP_400_BAD_REQUEST)
        position = get_object_or_404(Position, id=id)
        serializer = PositionSerializer(position)
        return Response(serializer.data)

    @action(detail=False, methods=['put'], url_path='replace',authentication_classes=[JWTAuthentication],permission_classes=[IsStaffPermission])
    def replace(self, request):
        # 不使用 pk，而是从请求数据中获取 id
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        position = get_object_or_404(Position, id=id)
        serializer = PositionSerializer(position, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['patch'], url_path='modify',authentication_classes=[JWTAuthentication],permission_classes=[IsStaffPermission])
    def modify(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        position = get_object_or_404(Position, id=id)
        serializer = PositionSerializer(position, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # [資安修補 HIGH-3] 刪除職位屬主檔維護，限管理員。
    @action(detail=False, methods=['post'], url_path='remove',authentication_classes=[JWTAuthentication],permission_classes=[IsStaffPermission])
    def remove(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        position = get_object_or_404(Position, id=id)
        position.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class GraduateViewSet(viewsets.ViewSet):
    """

    """
    @action(detail=False, methods=['get'], url_path='unique-grades',authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_unique_grades(self, request):
        """
        取得所有年級並由大到小排序
        """
        grades = Graduate.objects.values_list('grade', flat=True).distinct().order_by('-grade')
        return Response(grades)

    @action(detail=False, methods=['get'], url_path='get-all',authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_all(self, request):
        # [資安修補 SEC-008] 公開端點不得外洩學號（student_id 屬個資）。
        # 保留 id/school/grade 等非敏感欄位，學號僅供管理端（會員 admin 端點）取得。
        queryset = Graduate.objects.all()
        serializer = GraduateSerializer(queryset, many=True)
        data = serializer.data
        for item in data:
            item.pop('student_id', None)
        return Response(data)
    
    @action(detail=False, methods=['post'], url_path='create-new',authentication_classes=[JWTAuthentication],permission_classes=[IsStaffPermission])
    def create_new(self, request):
        serializer = GraduateSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='get-one',authentication_classes=[],permission_classes=[permissions.AllowAny])
    def get_one(self, request):
        id = request.query_params.get('id')
        if not id:
            return Response({'detail': '缺少 id 参数'}, status=status.HTTP_400_BAD_REQUEST)
        graduate = get_object_or_404(Graduate, id=id)
        serializer = GraduateSerializer(graduate)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='replace',authentication_classes=[JWTAuthentication],permission_classes=[IsStaffPermission])
    def replace(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        graduate = get_object_or_404(Graduate, id=id)
        serializer = GraduateSerializer(graduate, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='modify',authentication_classes=[JWTAuthentication],permission_classes=[IsStaffPermission])
    def modify(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        graduate = get_object_or_404(Graduate, id=id)
        serializer = GraduateSerializer(graduate, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # [資安修補 HIGH-4] 原本無任何權限類別 → 落到全域 AllowAny，未驗證者即可刪除畢業資料，
    # 而 Member.graduate 為 O2O CASCADE，會連帶刪除會員。改為限管理員。
    @action(detail=False, methods=['post'], url_path='remove',authentication_classes=[JWTAuthentication],permission_classes=[IsStaffPermission])
    def remove(self, request):
        id = request.data.get('id')
        if not id:
            return Response({'detail': '缺少 id 字段'}, status=status.HTTP_400_BAD_REQUEST)
        graduate = get_object_or_404(Graduate, id=id)
        graduate.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
