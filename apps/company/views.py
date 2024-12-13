from rest_framework import viewsets, status , permissions
from rest_framework.response import Response
from rest_framework.decorators import action , authentication_classes , permission_classes
from apps.member.models import Member
from apps.company.models import Company , Industry
from apps.company.serializer import CompanySerializer ,IndustrySerializer , SimpleCompanySerializer,CompanySearchSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework import generics
from django.db.models import Q

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CompanyListView_forAnyone(generics.ListAPIView):
    """For遊客的公司查詢"""
    serializer_class = CompanySearchSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="查詢公司資料，支持單一輸入值篩選多個欄位",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="全局搜尋關鍵字", type=openapi.TYPE_STRING),
            openapi.Parameter('industry', openapi.IN_QUERY, description="產業類別", type=openapi.TYPE_STRING),
        ],
        responses={200: CompanySerializer(many=True)}
    )
    def get_queryset(self):
        """
        根據單一查詢參數過濾公司資料。
        使用 `search` 進行多欄位查詢，並可額外根據產業篩選。
        """
        queryset = Company.objects.all()
        search = self.request.query_params.get('search', None)
        industry = self.request.query_params.get('industry', None)
        
        if industry and int(industry) != 0:
            queryset = queryset.filter(industry=industry)
            
        if search:
            query = (
            Q(name__icontains=search) |  # 公司名稱
            Q(member__name__icontains=search) |  # 系友名稱
            Q(member__position__title__icontains=search) |  # 職位標題
            Q(products__icontains=search) |  # 產品描述
            Q(description__icontains=search) | 
            Q(address__icontains=search) |  # 地址
            Q(email__icontains=search) |  # 電子郵件
            Q(phone_number__icontains=search)  # 電話號碼
            )
            queryset = queryset.filter(query)

        return queryset


class CompanyListView(generics.ListAPIView):
    """For管理端的公司查詢"""
    serializer_class = CompanySearchSerializer
    authentication_classes=[]
    permission_classes=[permissions.AllowAny]

    @swagger_auto_schema(
        operation_description="查詢公司資料，支持多個查詢參數進行篩選",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, description="公司名稱", type=openapi.TYPE_STRING),
            openapi.Parameter('member', openapi.IN_QUERY, description="會員 ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('positions', openapi.IN_QUERY, description="職位", type=openapi.TYPE_STRING),
            openapi.Parameter('products', openapi.IN_QUERY, description="產品名稱", type=openapi.TYPE_STRING),
            openapi.Parameter('address', openapi.IN_QUERY, description="地址", type=openapi.TYPE_STRING),
            openapi.Parameter('email', openapi.IN_QUERY, description="電子郵件", type=openapi.TYPE_STRING),
            openapi.Parameter('phone_number', openapi.IN_QUERY, description="電話號碼", type=openapi.TYPE_STRING),
        ],
        responses={200: CompanySerializer(many=True)}
    )
    def get_queryset(self):
        """
        根據查詢參數過濾公司資料。
        支持的查詢參數有：name, member, positions, products, address, email, phone_number。
        """
        queryset = Company.objects.all()
        name = self.request.query_params.get('name', None)
        industry = self.request.query_params.get('industry', None)
        member = self.request.query_params.get('member', None)
        positions = self.request.query_params.get('positions', None)
        products = self.request.query_params.get('products', None)
        address = self.request.query_params.get('address', None)
        email = self.request.query_params.get('email', None)
        phone_number = self.request.query_params.get('phone_number', None)

        query = Q()
        if name:
            query &= Q(name__icontains=name)
        if member:
            query &= Q(member=member)
        if positions:
            query &= Q(positions__icontains=positions)
        if products:
            query &= Q(products__icontains=products)
        if address:
            query &= Q(address__icontains=address)
        if email:
            query &= Q(email__icontains=email)
        if phone_number:
            query &= Q(phone_number__icontains=phone_number)
        if industry:
            query &= Q(industry = industry)

        return queryset.filter(query)

class CompanyViewSet(viewsets.ViewSet):
    """
    公司資料查詢
    """
    permission_classes=[permissions.IsAuthenticated]
    @swagger_auto_schema(
        operation_description="列出所有公司資料",
        responses={200: '成功返回公司列表'}
    )
    @action(methods=['get'],detail=False,authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def all(self, request):
        queryset = Company.objects.all()
        serializer = CompanySerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="建立新公司",
        request_body=CompanySerializer,
        responses={
            201: '公司創建成功',
            400: '請求無效'
        }
    )
    @action(methods=['post'],detail=False,authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def new(self, request):
        request.data['private'] = request.user.id
        request.data['member'] = Member.objects.get(private=request.user).id
        serializer = CompanySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="取得單一公司資料",
        responses={
            200: '成功返回公司資料',
            404: '公司不存在'
        }
    )
    @action(methods=['get'],detail=False,authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def selfInfo(self, request):
        try:
            company = Company.objects.get(member=Member.objects.get(private=request.user))
        except Company.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CompanySerializer(company)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="更新公司資料",
        request_body=CompanySerializer,
        responses={
            200: '公司更新成功',
            404: '公司不存在',
            400: '請求無效'
        }
    )
    @action(methods=['post'],detail=False,authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def selfChange(self, request):
        try:
            company = Company.objects.get(member=Member.objects.get(private=request.user))
        except Company.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除公司資料",
        responses={
            204: '公司刪除成功',
            404: '公司不存在'
        }
    )
    @action(methods=['delete'],detail=False,authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def delete(self, request):
        try:
            id = request.data.get("id")
            company = Company.objects.get(member=Member.objects.get(private=id))
        except Company.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def mostView(self, request):
        # Fetch top 10 companies with the highest click counts
        top_companies = Company.objects.order_by('-clicks')[:10]
        serializer = SimpleCompanySerializer(top_companies,many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def newUpload(self, request):
        # Fetch latest companies ordered by upload time (created_at)
        new_companies = Company.objects.order_by('-created_at')[:10]
        serializer = SimpleCompanySerializer(new_companies,many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=False, authentication_classes=[], permission_classes=[permissions.AllowAny])
    def randomCompanies(self, request):
        # Fetch 10 random companies
        random_companies = Company.objects.order_by('?')[:10]
        serializer = SimpleCompanySerializer(random_companies, many=True)
        return Response(serializer.data)

class IndustryViewSet(viewsets.ViewSet):
    """
    公司類別CRUD
    """
    permission_classes=[permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="列出所有行業資料",
        responses={200: '成功返回行業列表'}
    )
    @action(methods=['get'],detail=False,authentication_classes=[],permission_classes=[permissions.AllowAny])
    def all(self, request):
        queryset = Industry.objects.all()
        serializer = IndustrySerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="建立新行業",
        request_body=IndustrySerializer,
        responses={
            201: '行業創建成功',
            400: '請求無效'
        }
    )
    @action(methods=['post'],detail=False,authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAdminUser])
    def new(self, request):
        serializer = IndustrySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="取得單一行業資料",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="行業ID", type=openapi.TYPE_INTEGER)
        ],
        responses={
            200: '成功返回行業資料',
            400: '無參數',
            404: '行業不存在'
        }
    )
    @action(methods=['get'],detail=False,authentication_classes=[],permission_classes=[permissions.AllowAny])
    def getone(self, request):
        try:
            if request.data.get("id", '') == '':
                return Response(status=400, data="無參數")
            industry = Industry.objects.get(id=request.data.get('id'))
        except Industry.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = IndustrySerializer(industry)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="更新行業資料",
        request_body=IndustrySerializer,
        responses={
            200: '行業更新成功',
            400: '無參數或請求無效',
            404: '行業不存在'
        }
    )
    @action(methods=['put'],detail=False,authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAdminUser])
    def change(self, request):
        try:
            if request.data.get("id", '') == '':
                return Response(status=400, data="無參數")
            industry = Industry.objects.get(id=request.data.get('id'))
        except Industry.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = IndustrySerializer(industry, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除行業資料",
        responses={
            204: '行業刪除成功',
            400: '無參數',
            404: '行業不存在'
        }
    )
    @action(methods=['post'],detail=False,authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAdminUser])
    def delete(self, request):
        try:
            if request.data.get("id", '') == '':
                return Response(status=400, data="無參數")
            
            if request.data.get('id')=='1':
                return Response(status=400,data="此為預設值，無法刪除")
            
            industry = Industry.objects.get(id=request.data.get('id'))
        except Industry.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        industry.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)