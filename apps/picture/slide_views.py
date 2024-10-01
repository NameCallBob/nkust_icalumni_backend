from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.picture.models import SlideImage
from apps.picture.serializer import  SlideImageSerializer




# SlideImageViewSet
class SlideImageViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="取得所有的 SlideImage 資料",
        responses={200: SlideImageSerializer(many=True), 401: "未授權的用戶"},
    )
    def list(self, request):
        queryset = SlideImage.objects.all()
        serializer = SlideImageSerializer(queryset, many=True)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="創建一個新的 SlideImage",
        request_body=SlideImageSerializer,
        responses={
            201: openapi.Response('成功創建', SlideImageSerializer),
            400: '資料格式錯誤',
            401: '未授權的用戶',
        },
    )
    def create(self, request):
        serializer = SlideImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="根據 ID 取得指定的 SlideImage",
        responses={
            200: SlideImageSerializer,
            404: '找不到指定的 SlideImage',
            401: '未授權的用戶',
        },
    )
    def retrieve(self, request, pk=None):
        try:
            slide_image = SlideImage.objects.get(pk=pk)
        except SlideImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SlideImageSerializer(slide_image)
        return Response(serializer.data)

    @swagger_auto_schema(
        operation_description="更新指定的 SlideImage",
        request_body=SlideImageSerializer,
        responses={
            200: '成功更新',
            400: '資料格式錯誤',
            404: '找不到指定的 SlideImage',
            401: '未授權的用戶',
        },
    )
    def update(self, request):
        try:
            slide_image = SlideImage.objects.get(pk=pk)
        except SlideImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = SlideImageSerializer(slide_image, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        operation_description="刪除指定的 SlideImage",
        responses={
            204: '成功刪除',
            404: '找不到指定的 SlideImage',
            401: '未授權的用戶',
        },
    )
    def destroy(self, request, pk=None):
        try:
            slide_image = SlideImage.objects.get(pk=pk)
        except SlideImage.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        slide_image.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
