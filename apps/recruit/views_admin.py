from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from apps.recruit.models import Recruit
from apps.private.models import Private
from apps.company.models import Company
from .serializers_admin import RecruitSerializer, CompanySerializer, UserSerializer
from apps.private.cookie_auth import CookieJWTAuthentication as JWTAuthentication  # [資安修補 SEC-015] alias 成 cookie-aware 版本，向下相容 header 認證
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
import pandas as pd
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime
from rest_framework.permissions import IsAdminUser

class AdminPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class IsAdminOrSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and (request.user.is_staff or request.user.is_superuser)

class AdminRecruitViewSet(viewsets.ViewSet):
    permission_classes = [IsAdminOrSuperUser]
    authentication_classes = [JWTAuthentication]
    
    @swagger_auto_schema(
        operation_description="管理員取得所有招募職位",
        responses={
            200: openapi.Response('成功', RecruitSerializer(many=True)),
            401: '未授權',
            403: '權限不足'
        }
    )
    @action(methods=['get'], detail=False, url_path='admin/all_recruits')
    def all_recruits(self, request):
        queryset = Recruit.objects.all().order_by('-id')
        paginator = AdminPagination()
        page = paginator.paginate_queryset(queryset, request)
        
        if page is not None:
            serializer = RecruitSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)
        
        serializer = RecruitSerializer(queryset, many=True)
        return Response({'results': serializer.data})
    
    @swagger_auto_schema(
        operation_description="取得所有公司列表",
        responses={
            200: openapi.Response('成功', CompanySerializer(many=True)),
            401: '未授權',
            403: '權限不足'
        }
    )
    @action(methods=['get'], detail=False, url_path='admin/companies')
    def companies(self, request):
        companies = Company.objects.all().order_by('name')
        serializer = CompanySerializer(companies, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="取得所有用戶列表",
        responses={
            200: openapi.Response('成功', UserSerializer(many=True)),
            401: '未授權',
            403: '權限不足'
        }
    )
    @action(methods=['get'], detail=False, url_path='admin/users')
    def users(self, request):
        users = Private.objects.filter(is_active=True)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="取得單個招募職位詳情",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="職位 ID", type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={
            200: openapi.Response('成功', RecruitSerializer),
            400: '請求無效',
            404: '找不到職位',
            403: '權限不足'
        }
    )
    @action(methods=['get'], detail=False, url_path='admin/getOne')
    def get_one(self, request):
        recruit_id = request.query_params.get('id')
        if not recruit_id:
            return Response({"error": "請提供職位 ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            recruit = Recruit.objects.get(id=recruit_id)
        except Recruit.DoesNotExist:
            return Response({"error": "找不到該職位"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RecruitSerializer(recruit)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="創建新的招募職位",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='職位標題'),
                'intro': openapi.Schema(type=openapi.TYPE_STRING, description='職位介紹'),
                'release_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='發布日期'),
                'deadline': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='截止日期'),
                'contact': openapi.Schema(type=openapi.TYPE_OBJECT, description='聯絡人資料'),
                'images': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT), description='職位圖片'),
                'isPersonalContact': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否使用個人聯絡資料'),
                'isPersonalCompany': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否使用個人公司資料'),
                'company_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='公司ID'),
            },
            required=['title', 'intro', 'release_date', 'deadline']
        ),
        responses={
            201: openapi.Response('創建成功', RecruitSerializer),
            400: '請求無效',
            403: '權限不足'
        }
    )
    @action(methods=['post'], detail=False, url_path='admin/create')
    def create_recruit(self, request):
        serializer = RecruitSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="更新招募職位資料",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id': openapi.Schema(type=openapi.TYPE_INTEGER, description='職位 ID'),
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='職位標題'),
                'intro': openapi.Schema(type=openapi.TYPE_STRING, description='職位介紹'),
                'release_date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='發布日期'),
                'deadline': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='截止日期'),
                'contact': openapi.Schema(type=openapi.TYPE_OBJECT, description='聯絡人資料'),
                'images': openapi.Schema(type=openapi.TYPE_ARRAY, items=openapi.Schema(type=openapi.TYPE_OBJECT), description='職位圖片'),
                'isPersonalContact': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否使用個人聯絡資料'),
                'isPersonalCompany': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='是否使用個人公司資料'),
            }
        ),
        responses={
            200: openapi.Response('更新成功', RecruitSerializer),
            400: '請求無效',
            404: '找不到職位',
            403: '權限不足'
        }
    )
    @action(methods=['patch'], detail=False, url_path='admin/update')
    def update_recruit(self, request):
        recruit_id = request.data.get('id')
        if not recruit_id:
            return Response({"error": "請提供職位 ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            recruit = Recruit.objects.get(id=recruit_id)
        except Recruit.DoesNotExist:
            return Response({"error": "找不到該職位"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = RecruitSerializer(recruit, data=request.data, partial=True, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        operation_description="刪除招募職位",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="職位 ID", type=openapi.TYPE_INTEGER, required=True),
        ],
        responses={
            204: '刪除成功',
            400: '請求無效',
            404: '找不到職位',
            403: '權限不足'
        }
    )
    @action(methods=['delete'], detail=False, url_path='admin/delete')
    def delete_recruit(self, request):
        recruit_id = request.query_params.get('id')
        if not recruit_id:
            return Response({"error": "請提供職位 ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            recruit = Recruit.objects.get(id=recruit_id)
        except Recruit.DoesNotExist:
            return Response({"error": "找不到該職位"}, status=status.HTTP_404_NOT_FOUND)
        
        recruit.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @swagger_auto_schema(
        operation_description="匯出招募職位數據為Excel檔案",
        responses={
            200: '匯出成功',
            403: '權限不足'
        }
    )
    @action(methods=['get'], detail=False, url_path='admin/export')
    def export_data(self, request):
        recruits = Recruit.objects.all().order_by('-id')
        
        # 準備Excel數據
        data = []
        for recruit in recruits:
            company_name = recruit.contact.company_name if hasattr(recruit, 'contact') and recruit.contact else None
            user_name = recruit.company.member.name if recruit.company and hasattr(recruit.company, 'member') else None
            
            data.append({
                'ID': recruit.id,
                '職位名稱': recruit.title,
                '公司名稱': company_name,
                '發布者': user_name,
                '發布日期': recruit.release_date,
                '截止日期': recruit.deadline,
                '狀態': '啟用' if recruit.active else '停用',
                '簡介': recruit.intro,
            })
        
        # 創建DataFrame
        df = pd.DataFrame(data)
        
        # 創建Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='招募職位資料', index=False)
            
            # 調整欄寬