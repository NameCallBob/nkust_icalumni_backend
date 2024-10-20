from django.db.models import Q
from rest_framework import generics,permissions
from apps.product.serializer import ProductSerializer
from apps.product.models import Product
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    authentication_classes=[]
    permission_classes=[permissions.AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, description="產品名稱", type=openapi.TYPE_STRING),
            openapi.Parameter('company', openapi.IN_QUERY, description="所屬公司ID", type=openapi.TYPE_INTEGER),
            openapi.Parameter('created_at', openapi.IN_QUERY, description="建立日期", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
            openapi.Parameter('updated_at', openapi.IN_QUERY, description="更新日期", type=openapi.TYPE_STRING, format=openapi.FORMAT_DATE),
        ],
        responses={200: ProductSerializer(many=True)}
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        queryset = Product.objects.all()
        name = self.request.query_params.get('name', None)
        company = self.request.query_params.get('company', None)
        created_at = self.request.query_params.get('created_at', None)
        updated_at = self.request.query_params.get('updated_at', None)

        query = Q()
        if name:
            query &= Q(name__icontains=name)
        if company:
            query &= Q(company=company)
        if created_at:
            query &= Q(created_at=created_at)
        if updated_at:
            query &= Q(updated_at=updated_at)

        return queryset.filter(query)


class ProductViewSet(viewsets.ViewSet):
    """
    一個用於列出、檢索、創建、更新和刪除產品的 ViewSet。
    僅允許對當前用戶所屬的公司的產品進行操作。
    """
    
    @swagger_auto_schema(
        operation_summary="列出產品",
        operation_description="列出當前用戶所屬公司中的所有產品。",
        responses={200: ProductSerializer(many=True)},
    )
    def list(self, request):
        queryset = self.get_queryset()
        serializer = ProductSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="檢索產品",
        operation_description="根據ID檢索指定的產品。",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="產品ID", type=openapi.TYPE_INTEGER),
        ],
        responses={200: ProductSerializer()},
    )
    def retrieve(self, request):
        id = request.query_params.get("id", 0)
        product = get_object_or_404(self.get_queryset(), id=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_summary="創建產品",
        operation_description="創建一個新的產品，並將其分配給當前用戶所屬的公司。",
        request_body=ProductSerializer,
        responses={201: ProductSerializer()},
    )
    def create(self, request):
        data = request.data.copy()
        data['company'] = request.user.company.id  # 確保產品屬於當前用戶的公司
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="更新產品",
        operation_description="更新指定ID的產品的所有字段。",
        request_body=ProductSerializer,
        responses={200: ProductSerializer()},
    )
    def update(self, request):
        id = request.data.get("id", 0)
        product = get_object_or_404(self.get_queryset(), id=id)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="局部更新產品",
        operation_description="局部更新指定ID的產品。只更新提供的字段。",
        request_body=ProductSerializer(partial=True),
        responses={200: ProductSerializer()},
    )
    def partial_update(self, request):
        id = request.data.get("id", 0)
        product = get_object_or_404(self.get_queryset(), id=id)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_summary="刪除產品",
        operation_description="刪除指定ID的產品。",
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_QUERY, description="產品ID", type=openapi.TYPE_INTEGER),
        ],
        responses={204: 'No Content'},
    )
    def destroy(self, request):
        id = request.query_params.get("id", 0)
        product = get_object_or_404(self.get_queryset(), id=id)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
