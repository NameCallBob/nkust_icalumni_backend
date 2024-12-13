from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework.decorators import action , permission_classes , authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status

from apps.product.models import Product, ProductImage
from apps.product.serializer import ProductSerializer
from apps.company.models import Company

class ProductViewSet(ViewSet):
    """
    產品的CRUD操作
    """

    @action(methods=['post'], detail=False,
            authentication_classes=[JWTAuthentication] , permission_classes=[IsAuthenticated])
    def new(self, request):
        """
        新增產品
        """
        serializer = ProductSerializer(data=request.data)
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
        member_id = request.query_params.get('id')

        if not member_id:
            return Response({"error": "請提供系友ID"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            product = Product.objects.filter(company=Company.objects.get(member=Member.objects.get(private_id=member_id)) , is_active=True)
        except Product.DoesNotExist:
            return Response({"error": "找不到此產品"}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product , many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['get'], detail=False,
            authentication_classes=[JWTAuthentication] , permission_classes=[IsAuthenticated])
    def selfCompany(self,request):
        """
        取得自身公司的上下架商品
        """
        ob = Product.object.filter(company=Company.objects.get(member = request.user.member))

        serializer = ProductSerializer(ob , many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
        

    @action(methods=['put'], detail=False, 
            authentication_classes=[JWTAuthentication] , permission_classes=[IsAuthenticated])
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

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['patch'], detail=False,
            authentication_classes=[JWTAuthentication] , permission_classes=[IsAuthenticated])
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

        serializer = ProductSerializer(product, data=request.data, partial=True)
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
