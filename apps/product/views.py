from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action , permission_classes , authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny , IsAuthenticatedOrReadOnly
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from django.db.models import Q

from apps.product.models import Product, ProductImage , ProductCate
from apps.product.serializer import ProductSerializer , ProductCateSerializer
from apps.company.models import Company

class ProductViewSet(ViewSet):
    """
    產品的CRUD操作
    """

    @action(methods=['post'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[IsAuthenticated])
    def new(self, request):
        """
        新增產品
        """
        data = request.data.copy()
        try:
            # 自動填充 company
            data['company'] = Company.objects.get(member=request.user.member).id
        except Company.DoesNotExist:
            return Response({"error": "找不到與使用者相關的公司"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(methods=['get'], detail=False,
            authentication_classes=[JWTAuthentication] , permission_classes=[IsAuthenticated])
    def getOne(self, request):
        """
        取得單一產品資訊
        """
        product_id = request.query_params.get('id')
        if not product_id:
            return Response({"error": "請提供產品ID"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id=product_id,is_active = True)
        except Product.DoesNotExist:
            return Response({"error": "找不到此產品"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=False,
            authentication_classes=[] , permission_classes=[AllowAny])
    def member(self, request):
        """
        取得該公司的所以上架商品
        """
        from apps.member.models import Member
        member_id = request.query_params.get('member_id')
        category = request.query_params.get("category", "")

        if not member_id:
            return Response({"error": "請提供系友ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.filter(company=Company.objects.get(member_id=member_id) , is_active=True)
            # 按分類篩選
            if category:
                product = product.filter(category_id=category)
            
        except Product.DoesNotExist:
            return Response({"error": "找不到此產品"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product , many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(
        methods=['get'],
        detail=False,
        authentication_classes=[JWTAuthentication],
        permission_classes=[IsAuthenticated]
    )
    def selfCompany(self, request):
        """
        取得自身公司的上下架商品，支援分類篩選與關鍵字搜尋。
        """
        category = request.query_params.get("category", "")
        search = request.query_params.get("search", "")

        # 取得公司相關的商品
        try:
            company = Company.objects.get(member=request.user.member)
        except Company.DoesNotExist:
            return Response(
                {"error": "Company not found."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # 基本篩選條件
        products = Product.objects.filter(company=company)

        # 按分類篩選
        if category:
            products = products.filter(category_id=category)

        # 按關鍵字搜尋 (針對名稱或描述進行搜尋)
        if search:
            products = products.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )

        # 序列化資料
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['put'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[IsAuthenticated])
    def change(self, request):
        """
        更新產品資訊
        """
        product_id = request.data.get('id')
        if not product_id:
            return Response({"error": "請提供產品ID"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "找不到此產品"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        try:
            # 強制更新 company 為當前使用者的公司
            data['company'] = Company.objects.get(member=request.user.member).id
        except Company.DoesNotExist:
            return Response({"error": "找不到與使用者相關的公司"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(product, data=data, partial=False)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=['patch'], detail=False, authentication_classes=[JWTAuthentication], permission_classes=[IsAuthenticated])
    def partial_change(self, request):
        """
        部分更新產品資訊
        """
        product_id = request.data.get('id')
        if not product_id:
            return Response({"error": "請提供產品ID"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"error": "找不到此產品"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        try:
            # 強制更新 company 為當前使用者的公司
            data['company'] = Company.objects.get(member=request.user.member).id
        except Company.DoesNotExist:
            return Response({"error": "找不到與使用者相關的公司"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

    @action(methods=['delete'], detail=False, 
            authentication_classes=[JWTAuthentication] , permission_classes=[IsAuthenticated])
    def remove(self, request):
        """
        刪除產品
        """

        product_id = request.data.get('id')
        if not product_id:
            return Response({"error": "請提供產品ID"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = Product.objects.get(id=product_id)
            product.delete()
            return Response({"success": "產品已刪除"}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({"error": "找不到此產品"}, status=status.HTTP_404_NOT_FOUND)

from rest_framework import viewsets


class ProductCateViewSet(viewsets.ModelViewSet):
    """
    產品類別的視圖集
    提供依使用者 Token 或公司 ID 查詢功能
    """
    serializer_class = ProductCateSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        動態過濾分類：
        1. 若提供 company_id，則返回該公司相關分類。
        2. 若無 company_id 且使用者已登入，返回該使用者公司的分類。
        """
        from apps.company.models import Company
        user = self.request.user
        company_id = self.request.query_params.get('company_id', None)
        member_id = self.request.query_params.get('member_id', None)
        try:

            if member_id:
                # 根據 company_id 過濾
                return ProductCate.objects.filter(company_id=Company.objects.get(member_id=member_id).id).distinct()
        except Company.DoesNotExist:
            return Response("公司未知",status=404)
        if company_id:
            # 根據 company_id 過濾
            return ProductCate.objects.filter(company_id=company_id).distinct()

        if user.is_authenticated:
            # 返回登入用戶的公司相關分類
            return ProductCate.objects.filter(company=Company.objects.get(member=user.member)).distinct()

        # 未提供任何查詢條件，或未登入，返回空集
        return ProductCate.objects.none()

    def perform_create(self, serializer):
        """
        創建分類時自動關聯至當前使用者的公司
        """
        user = self.request.user
        if not user.is_authenticated:
            raise PermissionDenied("您必須登入才能創建分類。")
        serializer.save(company=Company.objects.get(member=user.member))