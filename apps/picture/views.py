from rest_framework import status, viewsets, permissions
from rest_framework.response import Response
from apps.picture.models import SelfImage, CompanyImage, ProductImage
from apps.picture.serializer import SelfImageSerializer, CompanyImageSerializer, ProductImageSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class SelfImageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="取得所有 SelfImage 資料",
        responses={200: SelfImageSerializer(many=True), 401: "未授權的用戶"}
    )
    def all(self, request):
        queryset = SelfImage.objects.all()
        serializer = SelfImageSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="取得當前使用者的 SelfImage 資料",
        responses={200: SelfImageSerializer(many=True), 401: "未授權的用戶"}
    )
    def selfInfo(self, request):
        queryset = SelfImage.objects.filter(member=request.user.member.id)
        serializer = SelfImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建 SelfImage",
        request_body=SelfImageSerializer,
        responses={201: openapi.Response('成功創建', SelfImageSerializer), 400: '格式錯誤', 401: '未授權'}
    )
    def new(self, request):
        serializer = SelfImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="更新 SelfImage",
        request_body=SelfImageSerializer,
        responses={200: '成功更新', 400: '格式錯誤', 404: '找不到', 401: '未授權'}
    )
    def change(self, request):
        try:
            image = SelfImage.objects.get(id=request.data.get("id"))
        except SelfImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SelfImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除 SelfImage",
        responses={204: '成功刪除', 404: '找不到', 401: '未授權'}
    )
    def delete(self, request):
        try:
            image = SelfImage.objects.get(id=request.data.get("id"))
        except SelfImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CompanyImageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="取得所有 CompanyImage 資料",
        responses={200: CompanyImageSerializer(many=True), 401: "未授權"}
    )
    def all(self, request):
        queryset = CompanyImage.objects.all()
        serializer = CompanyImageSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        operation_description="取得當前公司成員的 CompanyImage 資料",
        responses={200: CompanyImageSerializer(many=True), 401: "未授權"}
    )
    def selfInfo(self, request):
        queryset = CompanyImage.objects.filter(company=request.user.member.company.id)
        serializer = CompanyImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建 CompanyImage",
        request_body=CompanyImageSerializer,
        responses={201: openapi.Response('成功創建', CompanyImageSerializer), 400: '格式錯誤', 401: '未授權'}
    )
    def new(self, request):
        serializer = CompanyImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="更新 CompanyImage",
        request_body=CompanyImageSerializer,
        responses={200: '成功更新', 400: '格式錯誤', 404: '找不到', 401: '未授權'}
    )
    def change(self, request):
        try:
            image = CompanyImage.objects.get(id=request.data.get("id"))
        except CompanyImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = CompanyImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除 CompanyImage",
        responses={204: '成功刪除', 404: '找不到', 401: '未授權'}
    )
    def delete(self, request):
        try:
            image = CompanyImage.objects.get(id=request.data.get("id"))
        except CompanyImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ProductImageViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    @swagger_auto_schema(
        operation_description="取得所有 ProductImage 資料",
        responses={200: ProductImageSerializer(many=True), 401: "未授權"}
    )
    def all(self, request):
        queryset = ProductImage.objects.all()
        serializer = ProductImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建 ProductImage",
        request_body=ProductImageSerializer,
        responses={201: openapi.Response('成功創建', ProductImageSerializer), 400: '格式錯誤', 401: '未授權'}
    )
    def new(self, request):
        serializer = ProductImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="更新 ProductImage",
        request_body=ProductImageSerializer,
        responses={200: '成功更新', 400: '格式錯誤', 404: '找不到', 401: '未授權'}
    )
    def change(self, request):
        try:
            image = ProductImage.objects.get(id=request.data.get("id"))
        except ProductImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ProductImageSerializer(image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除 ProductImage",
        responses={204: '成功刪除', 404: '找不到', 401: '未授權'}
    )
    def delete(self, request):
        try:
            image = ProductImage.objects.get(id=request.data.get("id"))
        except ProductImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
