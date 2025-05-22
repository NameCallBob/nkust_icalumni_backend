from rest_framework import viewsets, status , permissions ,filters
from rest_framework.response import Response
from rest_framework.decorators import action , authentication_classes , permission_classes
from apps.member.models import Member
from apps.company.models import Company , Industry
from apps.company.serializer import CompanySerializer ,IndustrySerializer , SimpleCompanySerializer,CompanySearchSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.record.func import create_query_log,increment_query_frequency

from rest_framework import generics

from django.db.models import Count, Q, F
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework.pagination import PageNumberPagination

class CustomPagination(PageNumberPagination):
    page_size = 10  # 每頁顯示10筆資料
    page_size_query_param = 'page_size'
    max_page_size = 100

class CompanyListView_forAnyone(generics.ListAPIView):
    """For 遊客的公司查詢"""
    serializer_class = CompanySearchSerializer
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    pagination_class = CustomPagination  # 強制使用分頁
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']  # 預設排序

    def list(self, request, *args, **kwargs):
        search = request.query_params.get('search', None)
        industry = request.query_params.get('industry', None)
        
        # 使用搜索詞或行業作為搜索記錄
        search_term = search if search else industry
        ip = request.META.get('REMOTE_ADDR')
        
        # 增加搜索頻率計數
        if search_term:
            increment_query_frequency(query=search_term)        
            # 記錄搜索日誌
            create_query_log(query=search_term, ip=ip, search_type='general')

            
        # 檢查搜索詞是否為熱門搜索（可以在緩存中存儲和獲取）
        # if search_term:
        #     cache_key = f"hot_search:{search_term}"
        #     is_hot = cache.get(cache_key, False)
        #     if not is_hot and get_query_frequency(search_term) > 10:  # 假設熱門閾值為10
        #         cache.set(cache_key, True, 86400)  # 緩存一天
        
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="查詢公司資料，支持多種篩選條件",
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="全局搜尋關鍵字", type=openapi.TYPE_STRING),
            openapi.Parameter('industry', openapi.IN_QUERY, description="產業類別ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('sort', openapi.IN_QUERY, description="排序方式: name, -name, created_at, -created_at", type=openapi.TYPE_STRING),
            openapi.Parameter('member_position', openapi.IN_QUERY, description="系友職位關鍵詞", type=openapi.TYPE_STRING),
            openapi.Parameter('address', openapi.IN_QUERY, description="地址關鍵詞", type=openapi.TYPE_STRING),
            openapi.Parameter('min_year', openapi.IN_QUERY, description="最小畢業年份", type=openapi.TYPE_INTEGER),
            openapi.Parameter('max_year', openapi.IN_QUERY, description="最大畢業年份", type=openapi.TYPE_INTEGER),
        ],
        responses={200: CompanySearchSerializer(many=True)}
    )
    def get_queryset(self):
        """
        根據查詢參數過濾公司資料。
        使用 `search` 進行多欄位查詢，並可額外根據產業和其他條件篩選。
        若未提供搜尋條件，則回傳所有公司資料，並啟用分頁。
        """
        # 為了提高性能，先獲取基本查詢集
        queryset = Company.objects.all().select_related('industry', 'member').prefetch_related('member__graduate')
        
        # 獲取所有查詢參數
        search = self.request.query_params.get('search', None)
        industry = self.request.query_params.get('industry', None)
        member_position = self.request.query_params.get('member_position', None)
        address = self.request.query_params.get('address', None)
        min_year = self.request.query_params.get('min_year', None)
        max_year = self.request.query_params.get('max_year', None)
        sort = self.request.query_params.get('sort', None)
        
        # 應用行業篩選
        if industry and industry.isdigit() and int(industry) != 0:
            queryset = queryset.filter(industry_id=int(industry))
        
        # 應用位置篩選
        if address:
            queryset = queryset.filter(address__icontains=address)
        
        # 應用職位篩選
        if member_position:
            queryset = queryset.filter(member__position__title__icontains=member_position)
        
        # 應用畢業年份範圍篩選
        if min_year and min_year.isdigit():
            queryset = queryset.filter(member__graduate__grade__gte=int(min_year))
        if max_year and max_year.isdigit():
            queryset = queryset.filter(member__graduate__grade__lte=int(max_year))
        
        # 應用全局搜索
        if search:
            query = (
                Q(name__icontains=search) |  # 公司名稱
                Q(member__name__icontains=search) |  # 系友名稱
                Q(member__position__title__icontains=search) |  # 職位標題
                Q(products__icontains=search) |  # 產品描述
                Q(description__icontains=search) |  # 公司描述
                Q(address__icontains=search) |  # 地址
                Q(email__icontains=search) |  # 電子郵件
                Q(phone_number__icontains=search)  # 電話號碼
            )
            queryset = queryset.filter(query)
        
        # 應用自定義排序
        if sort:
            if sort == 'name':
                queryset = queryset.order_by('name')
            elif sort == '-name':
                queryset = queryset.order_by('-name')
            elif sort == 'created_at':
                queryset = queryset.order_by('created_at')
            elif sort == '-created_at':
                queryset = queryset.order_by('-created_at')
        
        # # 標記結果是否為熱門搜索項目
        # # 這只是在查詢集上添加一個註釋，不會影響前端
        # if search:
        #     cache_key = f"hot_search_count:{search}"
        #     hot_count = cache.get(cache_key)
        #     if hot_count is None:
        #         hot_count = get_query_frequency(search)
        #         cache.set(cache_key, hot_count, 3600)  # 緩存一小時
            
        #     # 這裡只是標記數據，不會影響現有前端
        #     # 如果需要實際使用，可以在serializer中添加相應字段
        #     queryset = queryset.annotate(search_frequency=Value(hot_count, output_field=models.IntegerField()))
        
        return queryset
    
    # 添加獲取熱門搜索的方法，但不會影響現有API
    @action(detail=False, methods=['get'])
    def hot_searches(self, request):
        """獲取熱門搜索詞"""
        cache_key = "hot_searches_list"
        hot_searches = cache.get(cache_key)
        
        if hot_searches is None:
            # 假設有一個獲取熱門搜索的函數
            hot_searches = get_hot_searches(limit=10)
            cache.set(cache_key, hot_searches, 3600)  # 緩存一小時
            
        return Response({"hot_searches": hot_searches})
    
    # 添加獲取相關行業的方法，但不會影響現有API
    @action(detail=False, methods=['get'])
    def related_industries(self, request):
        """根據搜索詞獲取相關行業"""
        search = request.query_params.get('search', None)
        if not search:
            return Response({"related_industries": []})
            
        cache_key = f"related_industries:{search}"
        related_industries = cache.get(cache_key)
        
        if related_industries is None:
            # 查詢與搜索詞相關的行業
            companies = Company.objects.filter(
                Q(name__icontains=search) | 
                Q(products__icontains=search) |
                Q(description__icontains=search)
            )
            industry_ids = companies.values('industry').annotate(
                count=Count('industry')
            ).order_by('-count')[:5]
            
            related_industries = []
            for item in industry_ids:
                industry_id = item['industry']
                if industry_id:
                    industry = Industry.objects.get(id=industry_id)
                    related_industries.append({
                        'id': industry.id,
                        'title': industry.title,
                        'count': item['count']
                    })
            
            cache.set(cache_key, related_industries, 3600)  # 緩存一小時
            
        return Response({"related_industries": related_industries})

# 為了提高查詢效率的輔助函數
def get_query_frequency(query):
    """獲取查詢詞的頻率"""
    # 假設我們有一個查詢日誌模型
    cache_key = f"query_frequency:{query}"
    frequency = cache.get(cache_key)
    
    if frequency is None:
        frequency = QueryLog.objects.filter(query=query).count()
        cache.set(cache_key, frequency, 3600)  # 緩存一小時
    
    return frequency

def get_hot_searches(limit=10):
    """獲取熱門搜索詞"""
    # 從查詢日誌中獲取熱門搜索詞
    hot_searches = QueryLog.objects.filter(
        created_at__gte=timezone.now() - timezone.timedelta(days=7)
    ).values('query').annotate(
        count=Count('query')
    ).order_by('-count')[:limit]
    
    return [item['query'] for item in hot_searches]

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
            return Response(status=status.HTTP_404_NOT_FOUND,data="使用者尚未登陸資料")
        except Member.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND,data="使用者跳過系友建立資料之過程")
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