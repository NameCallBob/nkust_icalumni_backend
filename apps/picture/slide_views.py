from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import status, viewsets , permissions
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.picture.models import SlideImage
from apps.picture.serializer import  SlideImageSerializer
from rest_framework.decorators import action
from rest_framework.decorators import permission_classes,authentication_classes

# SlideImageViewSet
class SlideImageViewSet(viewsets.ViewSet):


    @swagger_auto_schema(
        operation_description="取得所有的圖片",
        responses={200: SlideImageSerializer(many=True), 400: '錯誤的請求'},
    )
    @action(methods=['get'],detail=False,
            authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def all(self, request):  # 'list' 改名為 'all'
        queryset = SlideImage.objects.all()
        serializer = SlideImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="取得所有的圖片",
        responses={200: SlideImageSerializer(many=True), 400: '錯誤的請求'},
    )
    @action(methods=['get'],detail=False,
            authentication_classes=[],permission_classes=[permissions.AllowAny])
    def active(self, request):  # 'list' 改名為 'all'
        queryset = SlideImage.objects.filter(active=True)
        serializer = SlideImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建圖片",
        request_body=SlideImageSerializer,
        responses={
            201: openapi.Response('成功創建', SlideImageSerializer),
            400: '資料格式錯誤',
            403: '無權限創建',
        },
    )
    @action(methods=['post'],detail=False,
            authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def add(self, request):  # 'create' 改名為 'add'
        if not request.user.is_authenticated:
            return Response({"detail": "無權限創建"}, status=status.HTTP_403_FORBIDDEN)

        serializer = SlideImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="根據 ID 取得圖片",
        responses={
            200: SlideImageSerializer,
            404: '找不到圖片',
        },
    )
    @action(methods=['get'],detail=False,
            authentication_classes=[],permission_classes=[permissions.AllowAny])
    def getOne_active(self, request):  # 'retrieve' 改名為 'get'
        try:
            pk = request.GET['id']
            slide_image = SlideImage.objects.get(pk=pk , active=True)
        except SlideImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(data={"msg": "key?"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SlideImageSerializer(slide_image)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="根據 ID 取得圖片",
        responses={
            200: SlideImageSerializer,
            404: '找不到圖片',
        },
    )
    @action(methods=['get'],detail=False,
            authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def getOne_auth(self, request):  # 'retrieve' 改名為 'get'
        try:
            pk = request.GET['id']
            slide_image = SlideImage.objects.get(pk=pk)
        except SlideImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except KeyError:
            return Response(data={"msg": "key?"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = SlideImageSerializer(slide_image)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="更新圖片",
        request_body=SlideImageSerializer,
        responses={
            200: '成功更新',
            400: '資料格式錯誤',
            404: '找不到圖片',
            403: '無權限更新',
        },
    )
    @action(methods=['put'],detail=False,
            authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def change(self, request):
        if not request.user.is_authenticated:
            return Response({"detail": "無權限更新"}, status=status.HTTP_403_FORBIDDEN)

        try:
            pk = request.data.get('id')
            slide_image = SlideImage.objects.get(pk=pk)
        except SlideImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = SlideImageSerializer(slide_image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除圖片",
        responses={
            204: '成功刪除',
            404: '找不到圖片',
            403: '無權限刪除',
        },
    )
    @action(methods=['delete'],detail=False,
            authentication_classes=[JWTAuthentication],permission_classes=[permissions.IsAuthenticated])
    def remove(self, request):  # 'destroy' 改名為 'remove'
        if not request.user.is_authenticated:
            return Response({"detail": "無權限刪除"}, status=status.HTTP_403_FORBIDDEN)

        try:
            pk = request.data.get('id', None)
            if pk is None:
                return Response(data={"msg": "NO"}, status=status.HTTP_400_BAD_REQUEST)
            slide_image = SlideImage.objects.get(pk=pk)
        except SlideImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        slide_image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'], url_path='switch_active', permission_classes=[permissions.IsAuthenticated], authentication_classes=[JWTAuthentication])
    def switch_active(self, request):
        image_id = request.data.get("id")
        try:
            image = SlideImage.objects.get(id=image_id)
            image.active = not image.active
            image.save()
            return Response({"status": "active status toggled", "active": image.active}, status=status.HTTP_200_OK)
        except SlideImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)