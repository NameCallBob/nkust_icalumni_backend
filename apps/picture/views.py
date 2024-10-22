from rest_framework import status, viewsets , permissions
from rest_framework.response import Response
from apps.picture.models import SelfImage, CompanyImage, ProductImage, SlideImage
from apps.picture.serializer import SelfImageSerializer, CompanyImageSerializer, ProductImageSerializer, SlideImageSerializer

# drf_yasg
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class SelfImageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="取得所有的 SelfImage 資料",
        responses={200: SelfImageSerializer(many=True), 401: "未授權的用戶"},
    )
    def all(self, request):
        queryset = SelfImage.objects.all()
        serializer = SelfImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建一個新的 SelfImage",
        request_body=SelfImageSerializer,
        responses={
            201: openapi.Response('成功創建', SelfImageSerializer),
            400: '資料格式錯誤',
            401: '未授權的用戶',
        },
    )
    def create(self, request):
        serializer = SelfImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="根據 ID 取得指定的 SelfImage",
        responses={
            200: SelfImageSerializer,
            404: '找不到指定的 SelfImage',
            401: '未授權的用戶',
        },
    )
    def retrieve(self, request, pk=None):
        try:
            self_image = SelfImage.objects.get(pk=pk)
        except SelfImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SelfImageSerializer(self_image)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="更新指定的 SelfImage",
        request_body=SelfImageSerializer,
        responses={
            200: '成功更新',
            400: '資料格式錯誤',
            404: '找不到指定的 SelfImage',
            401: '未授權的用戶',
        },
    )
    def update(self, request, pk=None):
        try:
            self_image = SelfImage.objects.get(pk=pk)
        except SelfImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SelfImageSerializer(self_image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除指定的 SelfImage",
        responses={
            204: '成功刪除',
            404: '找不到指定的 SelfImage',
            401: '未授權的用戶',
        },
    )
    def destroy(self, request, pk=None):
        try:
            self_image = SelfImage.objects.get(pk=pk)
        except SelfImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        self_image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CompanyImageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="取得所有的 CompanyImage 資料",
        responses={200: CompanyImageSerializer(many=True), 401: "未授權的用戶"},
    )
    def list(self, request):
        queryset = CompanyImage.objects.all()
        serializer = CompanyImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建一個新的 CompanyImage",
        request_body=CompanyImageSerializer,
        responses={
            201: openapi.Response('成功創建', CompanyImageSerializer),
            400: '資料格式錯誤',
            401: '未授權的用戶',
        },
    )
    def create(self, request):
        serializer = CompanyImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="根據 ID 取得指定的 CompanyImage",
        responses={
            200: CompanyImageSerializer,
            404: '找不到指定的 CompanyImage',
            401: '未授權的用戶',
        },
    )
    def retrieve(self, request, pk=None):
        try:
            company_image = CompanyImage.objects.get(pk=pk)
        except CompanyImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyImageSerializer(company_image)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="更新指定的 CompanyImage",
        request_body=CompanyImageSerializer,
        responses={
            200: '成功更新',
            400: '資料格式錯誤',
            404: '找不到指定的 CompanyImage',
            401: '未授權的用戶',
        },
    )
    def update(self, request, pk=None):
        try:
            company_image = CompanyImage.objects.get(pk=pk)
        except CompanyImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyImageSerializer(company_image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除指定的 CompanyImage",
        responses={
            204: '成功刪除',
            404: '找不到指定的 CompanyImage',
            401: '未授權的用戶',
        },
    )
    def destroy(self, request, pk=None):
        try:
            company_image = CompanyImage.objects.get(pk=pk)
        except CompanyImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        company_image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductImageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(
        operation_description="取得所有的 ProductImage 資料",
        responses={200: ProductImageSerializer(many=True), 401: "未授權的用戶"},
    )
    def list(self, request):
        queryset = ProductImage.objects.all()
        serializer = ProductImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建一個新的 ProductImage",
        request_body=ProductImageSerializer,
        responses={
            201: openapi.Response('成功創建', ProductImageSerializer),
            400: '資料格式錯誤',
            401: '未授權的用戶',
        },
    )
    def create(self, request):
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="根據 ID 取得指定的 ProductImage",
        responses={
            200: ProductImageSerializer,
            404: '找不到指定的 ProductImage',
            401: '未授權的用戶',
        },
    )
    def retrieve(self, request, pk=None):
        try:
            product_image = ProductImage.objects.get(pk=pk)
        except ProductImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductImageSerializer(product_image)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="更新指定的 ProductImage",
        request_body=ProductImageSerializer,
        responses={
            200: '成功更新',
            400: '資料格式錯誤',
            404: '找不到指定的 ProductImage',
            401: '未授權的用戶',
        },
    )
    def update(self, request, pk=None):
        try:
            product_image = ProductImage.objects.get(pk=pk)
        except ProductImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductImageSerializer(product_image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除指定的 ProductImage",
        responses={
            204: '成功刪除',
            404: '找不到指定的 ProductImage',
            401: '未授權的用戶',
        },
    )
    def destroy(self, request, pk=None):
        try:
            product_image = ProductImage.objects.get(pk=pk)
        except ProductImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        product_image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

